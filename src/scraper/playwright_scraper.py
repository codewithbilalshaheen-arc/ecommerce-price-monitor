import logging
from typing import Dict, Any, Optional
from src.scraper.cleaner import clean_price, detect_currency, clean_title, check_availability
from src.scraper.bs4_scraper import BeautifulSoupScraper

logger = logging.getLogger(__name__)


class PlaywrightScraper:
    def __init__(self, timeout: int = 15000):
        self.timeout = timeout

    def scrape(
        self,
        url: str,
        price_selector: Optional[str] = None,
        title_selector: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Scrape dynamic JS web pages using Playwright."""
        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, timeout=self.timeout, wait_until="domcontentloaded")
                content = page.content()
                browser.close()

                bs4_scraper = BeautifulSoupScraper()
                return bs4_scraper.parse_html(content, price_selector, title_selector)
        except Exception as e:
            logger.warning(f"Playwright scraping failed for {url}: {e}. Falling back to BeautifulSoup.")
            bs4_scraper = BeautifulSoupScraper()
            return bs4_scraper.scrape(url, price_selector, title_selector)
