import asyncio
import aiohttp
from controllers.car_scraper import CarScraper


async def main():
    scraper = CarScraper()
    async with aiohttp.ClientSession() as session:
        scraper.session = session
        await scraper.scrape()

if __name__ == "__main__":
    asyncio.run(main())
