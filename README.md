# E-commerce Price Monitoring Scraper & Dashboard 🏷️📊

An automated, resilient e-commerce price monitoring solution built in Python. Track competitor prices, detect price drops or increases, receive automated alerts (Slack / Email), and analyze historical pricing positioning using an interactive Streamlit dashboard.

---

## 🌟 Key Features

- **Automated Price Scraping Engine:** Extract product title, current price, currency, and availability using `BeautifulSoup` and `Playwright` for dynamic sites.
- **Robust Extraction Fallbacks:** Supports user-defined CSS selectors, JSON-LD Schema.org metadata extraction, OpenGraph meta tags, and heuristic fallbacks.
- **Data Normalization & Cleaning:** Automatically parses and standardizes price text, currency codes, title strings, and availability status.
- **Structured Historical Storage:** SQL database (SQLite/PostgreSQL) tracking historical price entries and timestamped change logs.
- **Automated Change Detection & Alerting:** Triggers notifications via Slack Webhook or Email when price changes exceed configurable percentage thresholds.
- **Interactive Web Dashboard:** Built with Streamlit & Plotly:
  - 📊 **Price Comparison Page:** Visual price positioning indicators (Lowest, Pricier, Delta vs Our Store).
  - 📈 **Price History & Trends Page:** Interactive multi-competitor price line charts and CSV report exports.
  - ⚙️ **Product Configuration Page:** Manage tracked products, competitor URLs, and custom CSS selectors.
  - 🔔 **Alerts & Settings Page:** Adjust alert sensitivity thresholds and inspect past alert history.
- **CLI Utility:** Easily initialize DB, seed demo data, run scheduled scraping jobs, and export CSV reports from the terminal.

---

## 📁 Repository Structure

```
├── data/                       # Database files and exported reports
├── docs/                       # Project specifications (PRD, Architecture, UX/UI)
│   ├── PRD.md
│   ├── architecture.md
│   └── ux_ui_design.md
├── src/                        # Source code
│   ├── analytics/              # Change detection and alerting logic
│   │   ├── alerts.py
│   │   └── change_detector.py
│   ├── dashboard/              # Streamlit web application
│   │   └── app.py
│   ├── db/                     # Database models and session management
│   │   ├── models.py
│   │   ├── seed.py
│   │   └── session.py
│   ├── scraper/                # Scraping engine and cleaning utilities
│   │   ├── bs4_scraper.py
│   │   ├── cleaner.py
│   │   ├── engine.py
│   │   ├── mock_server.py
│   │   └── playwright_scraper.py
│   ├── cli.py                  # Command-line interface
│   └── config.py               # Global settings & environment configuration
├── tests/                      # Unit and integration test suite
│   ├── test_analytics.py
│   ├── test_cleaner.py
│   ├── test_db.py
│   └── test_scraper.py
├── .gitignore
├── pyproject.toml
├── README.md
└── requirements.txt
```

---

## 🛠️ Installation & Quickstart

### 1. Prerequisites
- Python 3.10+
- `pip`

### 2. Installation
```bash
# Clone repository
git clone https://github.com/codewithbilalshaheen-arc/ecommerce-price-monitor.git
cd ecommerce-price-monitor

# Install dependencies
pip install -r requirements.txt

# (Optional) Install Playwright browsers for dynamic JS site support
playwright install chromium
```

### 3. Initialize & Seed Demo Data
```bash
# Initialize DB tables and seed sample e-commerce data
python src/cli.py seed
```

### 4. Launch Web Dashboard
```bash
streamlit run src/dashboard/app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 💻 CLI Usage

The project includes a command-line interface for batch tasks and automation:

```bash
# Initialize database
python src/cli.py init-db

# Seed sample data
python src/cli.py seed

# Run scraping job across all active competitor URLs
python src/cli.py scrape

# Run scraping job with Playwright for dynamic sites and custom threshold
python src/cli.py scrape --playwright --threshold 5.0

# Export price history report to CSV
python src/cli.py export --output data/price_report.csv
```

---

## 🧪 Running Tests

Run the complete test suite with `pytest`:

```bash
pytest
```

---

## ⚙️ Configuration & Environment Variables

Create a `.env` file or export environment variables:

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | SQLAlchemy connection URL | `sqlite:///data/price_monitor.db` |
| `SLACK_WEBHOOK_URL` | Slack Incoming Webhook URL | `""` |
| `ALERT_EMAIL_RECIPIENT` | Target email for price alerts | `""` |
| `PRICE_CHANGE_THRESHOLD_PCT` | Minimum % change to trigger alert | `5.0` |
| `REQUEST_TIMEOUT` | Scraper HTTP timeout (seconds) | `15` |

---

## 📄 License

MIT License.
