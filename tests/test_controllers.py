import pytest
from unittest.mock import AsyncMock, patch
import aiohttp
from controllers.car_scraper import CarScraper
from utils.config import BASE


@pytest.fixture
def car_scraper():
    return CarScraper()

@pytest.mark.asyncio
async def test_fetch_failure(car_scraper):
    url = BASE

    # Mock the aiohttp.ClientSession.get method to raise an exception
    mock_response = AsyncMock()
    mock_response.raise_for_status.side_effect = aiohttp.ClientError("Failed to fetch data")

    with patch('aiohttp.ClientSession.get', return_value=mock_response):
        async with aiohttp.ClientSession() as session:
            car_scraper.session = session
            response = await car_scraper.fetch(url)

            # Ensure that response is None due to the failure
            assert response is None
            session.get.assert_called_once_with(url)
