from unittest.mock import MagicMock, patch

import aiohttp
import asyncio

from database.db_manager import DatabaseManager, logger
from models.car import Car
from utils.config import BASE, PAGES


class CarScraper:
    BASE_URL = BASE
    MAX_PAGES = PAGES

    def __init__(self, db_url='sqlite:///cars.sqlite'):
        self.session = None
        self.orm = DatabaseManager(db_url)

    async def fetch(self, url):
        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                json_data = await response.json()
                logger.info(f"Fetched data from {url}")
                return json_data
        except aiohttp.ClientError as e:
            logger.error(f"Failed to fetch data from {url}: {e}")
            return None

    def parse_ad(self, ad):
        detail = ad.get('detail', {})
        if not detail:
            logger.warning(f"Detail: {ad}")
            return None

        return {
            'url': f"https://bama.ir{detail.get('url', '')}",
            'title': detail.get('title', ''),
            'time': detail.get('time', ''),
            'year': detail.get('year', ''),
            'mileage': detail.get('mileage', ''),
            'location': detail.get('location', ''),
            'description': detail.get('description', ''),
            'image': detail.get('image', ''),
            'modified_date': detail.get('modified_date', '')
        }

    async def extract_and_store_data(self, json_data):
        ads = json_data.get('data', {}).get('ads', [])
        for ad in ads:
            car_data = self.parse_ad(ad)
            if car_data:
                self.orm.add_instance(Car, car_data)

    async def scrape(self):
        page_index = 1
        prev_data = None

        while page_index <= self.MAX_PAGES:
            url = f"{self.BASE_URL}{page_index}"
            # print(url)
            json_data = await self.fetch(url)
            if json_data:
                ads = json_data.get('data', {}).get('ads', [])
                print(ads)
                if not ads or ads == prev_data:
                    logger.info("No new data found or data is the same as the previous page. Stopping.")
                    break

                await self.extract_and_store_data(json_data)
                prev_data = ads
                page_index += 1
            else:
                logger.error(f"Failed to fetch data from {url}. Stopping.")
                break


@patch('controllers.car_scraper.aiohttp.ClientSession.get')
async def test_fetch(mock_get, mock_car_scraper):
    mock_response = MagicMock()
    mock_response.json = asyncio.coroutine(lambda: {'data': {'ads': []}})
    mock_get.return_value = mock_response

    result = await mock_car_scraper.fetch('https://bama.ir/test-url')

    assert result == {'data': {'ads': []}}

@patch('controllers.car_scraper.aiohttp.ClientSession.get')
def test_parse_ad(mock_car_scraper):
    ad = {
        'detail': {
            'url': '/test-url',
            'title': 'Test Car',
            'time': '2024-08-19',
            'year': '2020',
            'mileage': '10000',
            'location': 'Test Location',
            'description': 'Test Description',
            'image': 'https://bama.ir/test-image.jpg',
            'modified_date': '2024-08-19'
        }
    }
    parsed_data = mock_car_scraper.parse_ad(ad)

    expected_data = {
        'url': 'https://bama.ir/test-url',
        'title': 'Test Car',
        'time': '2024-08-19',
        'year': '2020',
        'mileage': '10000',
        'location': 'Test Location',
        'description': 'Test Description',
        'image': 'https://bama.ir/test-image.jpg',
        'modified_date': '2024-08-19'
    }

    assert parsed_data == expected_data
