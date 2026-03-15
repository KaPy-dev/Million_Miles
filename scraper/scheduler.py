import asyncio
import logging
import os

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from scraper import scrape_all

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

INTERVAL_HOURS = float(os.environ.get("SCRAPER_INTERVAL_HOURS", "1"))


async def run_scrape() -> None:
    await scrape_all()


async def main() -> None:
    """Главная асинхронная точка входа."""
    log.info("Scheduler starting — interval=%.1f h", INTERVAL_HOURS)

    await run_scrape()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        run_scrape,
        trigger=IntervalTrigger(hours=INTERVAL_HOURS),
        id="scrape_job",
        name="CarSensor scrape",
        replace_existing=True,
    )
    scheduler.start()

    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        log.info("Shutting down scheduler...")
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())