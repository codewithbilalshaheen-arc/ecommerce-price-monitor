import re
from typing import Optional


def clean_price(raw_text: Optional[str]) -> Optional[float]:
    if not raw_text:
        return None

    text = str(raw_text).replace("\xa0", " ").strip()

    if re.search(r"\d+\.\d{3},\d{2}", text) or re.search(r"\d+,\d{2}\s*(?:€|EUR)", text):
        match_eu = re.search(r"(\d{1,3}(?:\.\d{3})*(?:,\d{1,2}))", text)
        if match_eu:
            num_str = match_eu.group(1).replace(".", "").replace(",", ".")
            try:
                return float(num_str)
            except ValueError:
                pass

    match = re.search(r"(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)", text)
    if match:
        num_str = match.group(1).replace(",", "")
        try:
            return float(num_str)
        except ValueError:
            pass

    return None


def detect_currency(raw_text: Optional[str]) -> str:
    if not raw_text:
        return "USD"

    text = str(raw_text).upper()

    if "€" in text or "EUR" in text:
        return "EUR"
    if "£" in text or "GBP" in text:
        return "GBP"
    if "¥" in text or "JPY" in text or "RMB" in text:
        return "JPY"
    if "₹" in text or "INR" in text:
        return "INR"
    if "CAD" in text or "C$" in text:
        return "CAD"
    if "AUD" in text or "A$" in text:
        return "AUD"
    if "$" in text or "USD" in text:
        return "USD"

    return "USD"


def clean_title(raw_title: Optional[str]) -> str:
    if not raw_title:
        return "Unknown Product"
    title = re.sub(r"\s+", " ", str(raw_title)).strip()
    return title if title else "Unknown Product"


def check_availability(raw_text: Optional[str]) -> bool:
    if not raw_text:
        return True

    text = str(raw_text).lower()
    out_of_stock_keywords = [
        "out of stock",
        "sold out",
        "currently unavailable",
        "backorder",
        "item unavailable",
        "temporarily out of stock",
    ]

    for keyword in out_of_stock_keywords:
        if keyword in text:
            return False

    return True