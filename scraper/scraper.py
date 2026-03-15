from __future__ import annotations

import asyncio
import logging
import os
import re
import random
from datetime import datetime, timezone

from playwright.async_api import async_playwright, Page, TimeoutError as PWTimeout
from sqlalchemy.dialects.postgresql import insert as pg_insert

from db import Car, get_session, init_db
from translator import (
    translate_maker,
    translate_fuel,
    translate_transmission,
    translate_body_type,
    translate_color,
    translate_drive,
    normalize_year,
    normalize_mileage,
    normalize_price,
    normalize_displacement,
)

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

BASE_URL = "https://www.carsensor.net"
MAX_CARS_PER_PAGE = int(os.environ.get("SCRAPER_MAX_CARS_PER_PAGE", "60"))
MAX_PAGES = int(os.environ.get("SCRAPER_MAX_PAGES", "100000"))
REQUEST_DELAY = 3
DETAIL_TIMEOUT = 60000
PAGE_TIMEOUT = 60000


def _extract_source_id(url: str) -> str | None:
    m = re.search(r"/detail/([A-Z0-9]+)/", url)
    return m.group(1) if m else None


async def random_delay(min_sec=2, max_sec=5):
    delay = random.uniform(min_sec, max_sec)
    await asyncio.sleep(delay)


async def apply_stealth(page: Page):
    """Максимальная маскировка."""
    scripts = [
        "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });",
        "Object.defineProperty(navigator, 'plugins', { get: () => [{name: 'Chrome PDF Plugin'}, {name: 'Chrome PDF Viewer'}, {name: 'Native Client'}] });",
        "Object.defineProperty(navigator, 'languages', { get: () => ['ja-JP', 'ja', 'en-US', 'en'] });",
        "window.chrome = { runtime: {}, loadTimes: function() {}, csi: function() {}, app: {} };",
        "const originalQuery = window.navigator.permissions.query; window.navigator.permissions.query = (parameters) => (parameters.name === 'notifications' ? Promise.resolve({ state: Notification.permission }) : originalQuery(parameters));",
        "const getParameter = WebGLRenderingContext.prototype.getParameter; WebGLRenderingContext.prototype.getParameter = function(parameter) { if (parameter === 37445) return 'Intel Inc.'; if (parameter === 37446) return 'Intel Iris OpenGL Engine'; return getParameter(parameter); };",
        "const originalToDataURL = HTMLCanvasElement.prototype.toDataURL; HTMLCanvasElement.prototype.toDataURL = function(type) { if (this.width === 0 || this.height === 0) return originalToDataURL.call(this, type); const ctx = this.getContext('2d'); const imageData = ctx.getImageData(0, 0, this.width, this.height); return originalToDataURL.call(this, type); };",
    ]
    
    for script in scripts:
        try:
            await page.add_init_script(script)
        except:
            pass


async def scrape_single_page(page: Page, page_num: int) -> list[dict]:
    if page_num == 1:
        url = f"{BASE_URL}/usedcar/index.html"
    else:
        url = f"{BASE_URL}/usedcar/index{page_num}.html"
    
    log.info("Fetching page %d → %s", page_num, url)
    
    cars = []
    
    try:
        response = await page.goto(url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)
        
        if not response or response.status >= 400:
            log.error("Failed to load page %d: status=%s", page_num, response.status if response else "none")
            return []
        await asyncio.sleep(2)#4
        await page.evaluate("window.scrollTo(0, 300);")
        await asyncio.sleep(1)
        await page.evaluate("window.scrollTo(0, 600);")
        await asyncio.sleep(1)
        
        log.info("Page %d loaded, status: %s", page_num, response.status)
        
        title = await page.title()
        log.info("Page %d title: %s", page_num, title)
        
        content = await page.content()
        
        if response.status in [403, 429, 503]:
            log.error("HTTP %d on page %d", response.status, page_num)
            return []
        
        if any(x in content.lower() for x in ["recaptcha", "g-recaptcha", "captcha", "i'm not a robot"]):
            log.error("CAPTCHA detected on page %d", page_num)
            return []
        
        if "該当する車両は見つかりませんでした" in content:
            log.info("End of list on page %d", page_num)
            return []
        
    except Exception as e:
        log.error("Error loading page %d: %s", page_num, e)
        return []
    
    try:
        try:
            await page.wait_for_selector('a[href*="/detail/"]', timeout=5000)
        except:
            pass
        
        all_links = await page.query_selector_all('a')
        log.info("Found %d total links on page %d", len(all_links), page_num)
        
        car_urls = []
        for link in all_links:
            try:
                href = await link.get_attribute('href')
                if href and '/detail/' in href:
                    if href.startswith('/'):
                        href = f"{BASE_URL}{href}"
                    elif not href.startswith('http'):
                        href = f"{BASE_URL}/{href}"
                    
                    href = href.split('?')[0].split('#')[0]
                    
                    if href not in car_urls and '/usedcar/detail/' in href:
                        car_urls.append(href)
            except:
                continue
        
        log.info("Page %d: Found %d car URLs", page_num, len(car_urls))
        
    except Exception as e:
        log.error("Error finding links on page %d: %s", page_num, e)
        return []
    
    for url in car_urls[:MAX_CARS_PER_PAGE]:
        source_id = _extract_source_id(url)
        if source_id:
            cars.append({
                "source_id": source_id,
                "source_url": url,
                "page_num": page_num,
            })
    
    log.info("Page %d: Will process %d cars", page_num, len(cars))
    return cars


async def scrape_detail_page(page: Page, url: str) -> dict:
    try:
        log.info("Fetching detail: %s", url)
        
        response = await page.goto(url, wait_until="domcontentloaded", timeout=DETAIL_TIMEOUT)
        
        if not response or response.status >= 400:
            log.warning("Bad status %s for %s", response.status if response else "none", url)
            return {}
        
        await asyncio.sleep(2)#3
        
        data: dict = {}
        
        try:
            title = await page.title()
            data["page_title"] = title
            title_clean = title.replace("【中古車】", "").replace("｜カーセンサー", "").replace("｜carsensor", "")
            parts = title_clean.split()
            if len(parts) >= 2:
                data["maker_raw"] = parts[0]
                data["model_raw"] = " ".join(parts[1:3]) if len(parts) > 2 else parts[1]
        except Exception as e:
            log.debug("Error parsing title: %s", e)

        images = []
        try:
            img_els = await page.query_selector_all('img')
            for img in img_els:
                for attr in ['src', 'data-src', 'data-original']:
                    src = await img.get_attribute(attr)
                    if src and any(x in src for x in ['carsensor', 'csimg', 'autoc-one', 'ccsrpcma']):
                        if src.startswith('//'):
                            src = 'https:' + src
                        if src not in images and src.startswith('http'):
                            images.append(src)
                            break
        except Exception as e:
            log.debug("Error getting images: %s", e)
        
        data["images"] = images[:20]

        try:
            text = await page.inner_text('body')
            
            price_patterns = [
                r'([\d,]+)\s*万円',
                r'価格.*?([\d,]+)\s*万',
                r'([\d.]+)\s*万円',
            ]
            for pattern in price_patterns:
                match = re.search(pattern, text)
                if match:
                    price_str = match.group(1).replace(',', '')
                    data["price_raw"] = price_str + "万円"
                    break
            
            total_patterns = [
                r'総額\s*[:：]?\s*([\d,]+)\s*万円',
                r'支払総額\s*[:：]?\s*([\d,]+)\s*万円',
                r'総額.*?([\d,]+)\s*万円',
            ]
            for pattern in total_patterns:
                match = re.search(pattern, text)
                if match:
                    total_str = match.group(1).replace(',', '')
                    data["total_price_raw"] = total_str + "万円"
                    break
            
            year_match = re.search(r'(20\d{2})年', text)
            if year_match:
                data["year_raw"] = year_match.group(1) + "年"
            
            mileage_match = re.search(r'([\d.]+)\s*万km', text)
            if mileage_match:
                data["mileage_raw"] = mileage_match.group(0)
            
            colors = ['ホワイト', 'ブラック', 'シルバー', 'グレー', 'レッド', 'ブルー', 'グリーン', 
                     'ブラウン', 'ゴールド', 'ベージュ', 'イエロー', 'オレンジ', 'パープル', 'ピンク', 'パール']
            for color in colors:
                if color in text:
                    data["color_raw"] = color
                    break
            
            fuels = ['ガソリン', 'ハイブリッド', 'ディーゼル', '電気', 'LPG']
            for fuel in fuels:
                if fuel in text:
                    data["fuel_raw"] = fuel
                    break
                    
        except Exception as e:
            log.debug("Error parsing text: %s", e)

        spec_map = {}
        try:
            for selector in ['dt', 'th', '.spec-label', '[class*="spec"] dt']:
                elements = await page.query_selector_all(selector)
                for el in elements:
                    try:
                        key = await el.inner_text()
                        key = key.strip()
                        
                        next_sel = 'dd' if selector == 'dt' else 'td'
                        parent = await el.evaluate_handle('el => el.parentElement')
                        if parent:
                            value_el = await parent.query_selector(next_sel)
                            if value_el:
                                value = await value_el.inner_text()
                                spec_map[key] = value.strip()
                    except:
                        continue
        except Exception as e:
            log.debug("Error parsing specs: %s", e)
        
        data["raw_spec_map"] = spec_map

        key_map = {
            "年式": "year_raw",
            "初度登録": "year_raw",
            "走行距離": "mileage_raw",
            "車体色": "color_raw",
            "色": "color_raw",
            "燃料": "fuel_raw",
            "ミッション": "trans_raw",
            "ボディタイプ": "body_raw",
            "排気量": "displacement_raw",
            "駆動方式": "drive_raw",
            "ドア": "doors_raw",
            "乗車定員": "seats_raw",
            "修復歴": "accident_raw",
            "所在地": "location_raw",
        }

        for jp_key, field in key_map.items():
            for spec_key, spec_val in spec_map.items():
                if jp_key in spec_key:
                    data[field] = spec_val
                    break

        return data
        
    except Exception as e:
        log.error("Error scraping detail %s: %s", url, e)
        return {}


async def process_car(page, car_data, total_saved_ref):
    """Обрабатывает одну машину."""
    try:
        detail = await scrape_detail_page(page, car_data["source_url"])
        
        if not detail:
            log.warning("No detail for %s", car_data["source_id"])
            return False
        
        merged = {**car_data, **detail}
        
        maker = translate_maker(merged.get("maker_raw", ""))
        model_raw = merged.get("model_raw", "")
        
        model_parts = model_raw.split(" ", 1) if model_raw else ["", ""]
        model = model_parts[0].strip() if model_parts[0] else None
        grade = model_parts[1].strip() if len(model_parts) > 1 else None
        
        year = normalize_year(merged.get("year_raw", ""))
        mileage = normalize_mileage(merged.get("mileage_raw", ""))
        price = normalize_price(merged.get("price_raw", ""))
        total_price = normalize_price(merged.get("total_price_raw", ""))
        
        color = translate_color(merged.get("color_raw", ""))
        fuel = translate_fuel(merged.get("fuel_raw", ""))
        trans = translate_transmission(merged.get("trans_raw", ""))
        body = translate_body_type(merged.get("body_raw", ""))
        displacement = normalize_displacement(merged.get("displacement_raw", ""))
        drive = translate_drive(merged.get("drive_raw", ""))
        
        doors = None
        seats = None
        if merged.get("doors_raw"):
            m = re.search(r"\d+", str(merged["doors_raw"]))
            doors = int(m.group()) if m else None
        if merged.get("seats_raw"):
            m = re.search(r"\d+", str(merged["seats_raw"]))
            seats = int(m.group()) if m else None
        
        has_accident = None
        accident_raw = merged.get("accident_raw", "")
        if accident_raw:
            if any(x in accident_raw for x in ["無", "なし"]):
                has_accident = False
            elif any(x in accident_raw for x in ["有", "あり"]):
                has_accident = True
        
        db_data = dict(
            source_id=merged["source_id"],
            source_url=merged["source_url"],
            maker=maker,
            model=model,
            grade=grade,
            year=year,
            mileage_km=mileage,
            price_jpy=price,
            total_price_jpy=total_price,
            color=color,
            fuel_type=fuel,
            transmission=trans,
            body_type=body,
            displacement_cc=displacement,
            drive=drive,
            doors=doors,
            seats=seats,
            condition_score=None,
            has_accident=has_accident,
            location=merged.get("location_raw"),
            shop_name=merged.get("shop_name"),
            images=merged.get("images", []),
            equipment=merged.get("equipment", {}),
            raw_data={
                "spec_map": merged.get("raw_spec_map", {}),
                "page_title": merged.get("page_title", ""),
                "page_num": merged.get("page_num", 1),
            },
            scraped_at=datetime.now(timezone.utc),
        )
        
        async with get_session() as session:
            stmt = (
                pg_insert(Car)
                .values(**db_data)
                .on_conflict_do_update(
                    constraint="uq_cars_source_id",
                    set_={k: v for k, v in db_data.items() if k != "source_id"},
                )
            )
            await session.execute(stmt)
            await session.commit()
            total_saved_ref[0] += 1
            log.info("✓ Upserted: %s %s (%s) — %d yen [Page %d]",
                     maker or "Unknown", model or "Unknown", 
                     year or "N/A", price or 0, car_data.get("page_num", 1))
        
        return True
        
    except Exception as exc:
        log.error("Failed to process car %s: %s", 
                 car_data.get("source_id", "?"), exc)
        return False


async def scrape_all() -> None:
    log.info("=== Scrape run started ===")
    await init_db()

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
                "--disable-extensions",
                "--disable-plugins",
                "--disable-background-networking",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--disable-features=TranslateUI",
                "--disable-ipc-flooding-protection",
                "--js-flags=--max-old-space-size=4096",
            ],
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1440, "height": 900},
            screen={"width": 1440, "height": 900},
            locale="ja-JP",
            timezone_id="Asia/Tokyo",
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "ja-JP,ja;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
            },
        )
        
        await context.add_cookies([
            {
                "name": "visited",
                "value": "true",
                "domain": ".carsensor.net",
                "path": "/",
            },
            {
                "name": "cookieConsent",
                "value": "accepted",
                "domain": ".carsensor.net",
                "path": "/",
            }
        ])
        
        page = await context.new_page()
        await apply_stealth(page)
        
        total_saved = [0]
        page_num = 5
        empty_pages_count = 0
        max_empty_pages = 5
        
        while True:
            if MAX_PAGES > 0 and page_num > MAX_PAGES:
                log.info("Reached MAX_PAGES limit: %d", MAX_PAGES)
                break
            
            cars = await scrape_single_page(page, page_num)
            
            if not cars:
                empty_pages_count += 1
                log.info("Page %d empty (%d/%d)", page_num, empty_pages_count, max_empty_pages)
                if empty_pages_count >= max_empty_pages:
                    log.info("Stopping: %d empty pages", max_empty_pages)
                    break
            else:
                empty_pages_count = 0
            
            for i, car_data in enumerate(cars):
                log.info("Processing %d/%d on page %d: %s", 
                        i+1, len(cars), page_num, car_data["source_id"])
                await process_car(page, car_data, total_saved)
                await random_delay(2, 4)
            
            page_num += 1
            await random_delay(3, 6)
            
            if page_num % 5 == 0:
                log.info("Long pause...")
                await asyncio.sleep(random.uniform(5, 8))
        
        await browser.close()
    
    log.info("=== Scrape run done — %d cars upserted ===", total_saved[0])


if __name__ == "__main__":
    asyncio.run(scrape_all())