import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from src.db.session import get_db
from src.db.models import Product, CompetitorUrl, PriceLog
from src.scraper.bs4_scraper import BeautifulSoupScraper
from src.scraper.playwright_scraper import PlaywrightScraper
from src.analytics.change_detector import detect_price_change_and_alert

logger = logging.getLogger(__name__)


class ScrapingEngine:
    def __init__(self, use_playwright: bool = False):
        self.use_playwright = use_playwright
        self.bs4_scraper = BeautifulSoupScraper()
        self.playwright_scraper = PlaywrightScraper() if use_playwright else None

    def scrape_url(self, comp_url: CompetitorUrl) -> Dict[str, Any]:
        """Scrape a single CompetitorUrl using appropriate scraper."""
        url = comp_url.url
        price_sel = comp_url.css_selector_price
        title_sel = comp_url.css_selector_title

        if self.use_playwright and self.playwright_scraper:
            return self.playwright_scraper.scrape(url, price_sel, title_sel)
        else:
            return self.bs4_scraper.scrape(url, price_sel, title_sel)

    def run_job_for_url(self, comp_url_id: int, threshold_pct: float = 5.0) -> Optional[PriceLog]:
        """Scrape a single URL ID and save results to DB."""
        with get_db() as db:
            comp_url = db.query(CompetitorUrl).get(comp_url_id)
            if not comp_url or not comp_url.is_active:
                return None

            now = datetime.now(timezone.utc)
            try:
                data = self.scrape_url(comp_url)

                if data.get("price") is None:
                    comp_url.last_status = "FAILED"
                    comp_url.last_error = "Could not extract price"
                    comp_url.last_scraped_at = now
                    logger.error(f"Failed to extract price for {comp_url.url}")
                    return None

                # Update competitor URL status
                comp_url.last_status = "SUCCESS"
                comp_url.last_error = None
                comp_url.last_scraped_at = now

                # Add price log entry
                price_log = PriceLog(
                    product_id=comp_url.product_id,
                    competitor_url_id=comp_url.id,
                    scraped_title=data.get("title"),
                    raw_price_text=data.get("raw_price_text"),
                    price=data.get("price"),
                    currency=data.get("currency", "USD"),
                    is_available=data.get("is_available", True),
                    scraped_at=now,
                )
                db.add(price_log)
                db.flush()

                # Check for significant price changes and create alert if needed
                detect_price_change_and_alert(db, comp_url, price_log, threshold_pct=threshold_pct)

                return price_log

            except Exception as e:
                logger.error(f"Error scraping {comp_url.url}: {e}")
                comp_url.last_status = "FAILED"
                comp_url.last_error = str(e)
                comp_url.last_scraped_at = now
                return None

    def run_all(self, threshold_pct: float = 5.0) -> List[PriceLog]:
        """Scrape all active competitor URLs in database."""
        results = []
        with get_db() as db:
            active_urls = db.query(CompetitorUrl).filter(CompetitorUrl.is_active == True).all()
            url_ids = [u.id for u in active_urls]

        for url_id in url_ids:
            res = self.run_job_for_url(url_id, threshold_pct=threshold_pct)
            if res:
                results.append(res)

        return results
