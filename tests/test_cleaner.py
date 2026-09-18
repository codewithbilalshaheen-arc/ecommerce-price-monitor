from src.scraper.cleaner import clean_price, detect_currency, clean_title, check_availability


def test_clean_price():
    assert clean_price("$299.99") == 299.99
    assert clean_price("USD 1,249.50") == 1249.50
    assert clean_price("1.299,00 €") == 1299.00
    assert clean_price("£89") == 89.0
    assert clean_price("Free") is None
    assert clean_price(None) is None


def test_detect_currency():
    assert detect_currency("$99.99") == "USD"
    assert detect_currency("100 €") == "EUR"
    assert detect_currency("£50.00") == "GBP"
    assert detect_currency("¥5000") == "JPY"
    assert detect_currency("CAD 150") == "CAD"
    assert detect_currency(None) == "USD"


def test_clean_title():
    assert clean_title("  Wireless   Headphones\n  X1  ") == "Wireless Headphones X1"
    assert clean_title("") == "Unknown Product"
    assert clean_title(None) == "Unknown Product"


def test_check_availability():
    assert check_availability("In Stock and ready to ship") is True
    assert check_availability("Item is Currently Out of Stock") is False
    assert check_availability("Sold out - check back later") is False
    assert check_availability(None) is True
