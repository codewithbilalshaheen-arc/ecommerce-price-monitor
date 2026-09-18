import pytest
from src.scraper.bs4_scraper import BeautifulSoupScraper
from src.scraper.mock_server import start_mock_server


@pytest.fixture(scope="module")
def mock_server():
    server = start_mock_server(host="127.0.0.1", port=8989)
    yield server
    server.shutdown()


def test_parse_json_ld_schema():
    html = """
    <html>
    <head>
        <script type="application/ld+json">
        {
            "@type": "Product",
            "name": "Sony WH-1000XM5",
            "offers": {
                "price": "348.00",
                "priceCurrency": "USD"
            }
        }
        </script>
    </head>
    </html>
    """
    scraper = BeautifulSoupScraper()
    result = scraper.parse_html(html)

    assert result["title"] == "Sony WH-1000XM5"
    assert result["price"] == 348.00
    assert result["currency"] == "USD"


def test_parse_custom_selector():
    html = """
    <html>
    <body>
        <h1 class="my-title">Custom Item Title</h1>
        <div class="my-price">$123.45</div>
    </body>
    </html>
    """
    scraper = BeautifulSoupScraper()
    result = scraper.parse_html(
        html,
        price_selector=".my-price",
        title_selector=".my-title",
    )

    assert result["title"] == "Custom Item Title"
    assert result["price"] == 123.45


def test_mock_server_scraping(mock_server):
    scraper = BeautifulSoupScraper()

    # Headphones page
    headphones_res = scraper.scrape("http://127.0.0.1:8989/headphones")
    assert headphones_res["price"] == 279.99
    assert headphones_res["title"] == "Wireless Noise-Canceling Headphones X1"

    # Watch page
    watch_res = scraper.scrape(
        "http://127.0.0.1:8989/watch",
        price_selector="#price-tag",
        title_selector="#title",
    )
    assert watch_res["price"] == 185.50
    assert watch_res["title"] == "Smart Fitness Watch Series 5"

    # Out of stock page
    out_res = scraper.scrape("http://127.0.0.1:8989/out-of-stock")
    assert out_res["is_available"] is False
