import logging

# Setup logging
logger = logging.getLogger(__name__)


class CarScraper:
    BASE_URL = "https://bama.ir/cad/api/search?pageIndex="
    MAX_PAGES = 60

    def __init__(self):
        self.session = None

    async def fetch(self, url):
        pass

    def parse_ad(self, ad):
        pass

    async def extract_and_store_data(self, json_data):
        pass

    async def scrape(self):
        pass
