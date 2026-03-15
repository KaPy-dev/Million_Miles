from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--window-size=1920,1080")
options.add_argument("--lang=ja")                   
options.add_argument("--no-sandbox")                

driver = webdriver.Chrome(options=options)

try:
    driver.get("https://www.carsensor.net/")

    wait = WebDriverWait(driver, 20)

    possible_selectors = [
        ".cassetteitem",                    
        "li.cassetteitem",
        ".cassetteitem--car",
        ".item",
        ".cassetteList li",
        '[class*="cassette"]',
        '[data-item-id]',
        ".productList li",
    ]

    first_card = None

    for selector in possible_selectors:
        try:
            print(f"Trying selector: {selector}")
            first_card = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            print(f"→ SUCCESS with: {selector}")
            break
        except:
            print(f"→ not found: {selector}")
            continue

    if not first_card:
        print("None of the selectors worked → page is probably empty / blocked / changed")
        print("Saving screenshot and source for debug...")
        driver.save_screenshot("debug.png")
        with open("debug.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        raise Exception("No listing elements found")

    try:
        wait.until(EC.invisibility_of_element_located(
            (By.CSS_SELECTOR, ".loading, .spinner, .c-loading")
        ))
        print("Loader disappeared")
    except:
        pass

    items = driver.find_elements(By.CSS_SELECTOR, ".cassetteitem")

    for item in items:
        try:
            title = item.find_element(By.CSS_SELECTOR, ".cassetteitem_content-title, h3 a, .item-name").text.strip()
            price = item.find_element(By.CSS_SELECTOR, ".cassetteitem_other-price, .price, [class*='price']").text.strip()
            print(f"{title:<60} {price}")
        except:
            continue  

finally:
    driver.quit()