from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

MOCK_HTML_PAGES = {
    "/headphones": """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Wireless Headphones X1 - Store</title>
            <script type="application/ld+json">
            {
                "@type": "Product",
                "name": "Wireless Noise-Canceling Headphones X1",
                "offers": {
                    "price": "279.99",
                    "priceCurrency": "USD",
                    "availability": "https://schema.org/InStock"
                }
            }
            </script>
        </head>
        <body>
            <h1 class="product-title">Wireless Noise-Canceling Headphones X1</h1>
            <div class="price">$279.99</div>
        </body>
        </html>
    """,
    "/watch": """
        <!DOCTYPE html>
        <html>
        <head><title>Fitness Watch</title></head>
        <body>
            <h1 id="title">Smart Fitness Watch Series 5</h1>
            <span id="price-tag">$185.50</span>
        </body>
        </html>
    """,
    "/out-of-stock": """
        <!DOCTYPE html>
        <html>
        <body>
            <h1 class="product-title">Gaming Laptop 15</h1>
            <div class="price">$1,299.00</div>
            <p>Status: Out of Stock</p>
        </body>
        </html>
    """,
}


class MockHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in MOCK_HTML_PAGES:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(MOCK_HTML_PAGES[self.path].encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress HTTP server output in test logs


def start_mock_server(host="127.0.0.1", port=8989) -> HTTPServer:
    """Start local HTTP server in a background daemon thread."""
    server = HTTPServer((host, port), MockHTTPRequestHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    time.sleep(0.1)
    return server
