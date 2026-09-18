import json
import logging
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional

from src.config import DEFAULT_USER_AGENT, REQUEST_TIMEOUT
from src.scraper.cleaner import clean_price, detect_currency, clean_title, check_availability

logger = logging.getLogger(__name__)


class BeautifulSoupScraper:
    def __init__(self, user_agent: Optional[str] = None, timeout: int = REQUEST_TIMEOUT):
        self.headers = {
            "User-Agent": user_agent or DEFAULT_USER_AGENT,
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        self.timeout = timeout

    def fetch_page(self, url: str) -> str:
        """Fetch HTML content for a given URL."""
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        return response.text

    def parse_html(
        self,
        html_content: str,
        price_selector: Optional[str] = None,
        title_selector: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Extract title, price, currency, and availability from HTML content."""
        soup = BeautifulSoup(html_content, "html.parser")

        title = None
        price = None
        currency = "USD"
        raw_price_text = None
        is_available = True

        # 1. Try explicit user-provided CSS selectors if supplied
        if price_selector:
            p_elem = soup.select_one(price_selector)
            if p_elem:
                raw_price_text = p_elem.get_text()
                price = clean_price(raw_price_text)
                currency = detect_currency(raw_price_text)

        if title_selector:
            t_elem = soup.select_one(title_selector)
            if t_elem:
                title = clean_title(t_elem.get_text())

        # 2. Try JSON-LD schema.org metadata if price/title not yet found
        if not price or not title:
            json_ld_tags = soup.find_all("script", type="application/ld+json")
            for tag in json_ld_tags:
                try:
                    data = json.loads(tag.string)
                    # Support list of items or dict
                    items = data if isinstance(data, list) else [data]
                    for item in items:
                        if item.get("@type") in ("Product", "IndividualProduct"):
                            if not title and "name" in item:
                                title = clean_title(item["name"])
                            offers = item.get("offers", {})
                            if isinstance(offers, list) and offers:
                                offers = offers[0]
                            if isinstance(offers, dict) and not price:
                                p_val = offers.get("price") or offers.get("lowPrice")
                                if p_val:
                                    price = float(p_val)
                                    raw_price_text = str(p_val)
                                if "priceCurrency" in offers:
                                    currency = offers["priceCurrency"]
                                if offers.get("availability") and "OutOfStock" in offers["availability"]:
                                    is_available = False
                except Exception:
                    continue

        # 3. Fallback to common meta tags (og:title, og:price:amount, product:price:amount)
        if not title:
            meta_title = (
                soup.find("meta", property="og:title")
                or soup.find("meta", attrs={"name": "title"})
                or soup.find("title")
            )
            if meta_title:
                title = clean_title(meta_title.get("content") or meta_title.get_text())

        if not price:
            meta_price = (
                soup.find("meta", property="og:price:amount")
                or soup.find("meta", property="product:price:amount")
                or soup.find("meta", attrs={"name": "twitter:data1"})
            )
            if meta_price:
                raw_price_text = meta_price.get("content")
                price = clean_price(raw_price_text)
                currency = detect_currency(raw_price_text)

        # 4. Heuristic class/id fallback selectors for e-commerce sites
        if not price:
            common_price_classes = [
                ".price", "#price", ".product-price", ".our-price",
                ".a-price-whole", ".offer-price", "[data-price]",
                ".price-box", ".current-price", ".sales-price"
            ]
            for selector in common_price_classes:
                elem = soup.select_one(selector)
                if elem:
                    txt = elem.get_text()
                    parsed = clean_price(txt)
                    if parsed:
                        price = parsed
                        raw_price_text = txt
                        currency = detect_currency(txt)
                        break

        if not title:
            common_title_classes = [
                "h1", ".product-title", ".product-name", "#productTitle"
            ]
            for selector in common_title_classes:
                elem = soup.select_one(selector)
                if elem:
                    title = clean_title(elem.get_text())
                    if title:
                        break

        # Availability check on full page body text
        is_available = check_availability(soup.get_text())

        return {
            "title": title or "Unknown Product",
            "price": price,
            "currency": currency,
            "raw_price_text": raw_price_text,
            "is_available": is_available,
        }

    def scrape(
        self,
        url: str,
        price_selector: Optional[str] = None,
        title_selector: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Fetch URL and parse product information."""
        html = self.fetch_page(url)
        return self.parse_html(html, price_selector, title_selector)
