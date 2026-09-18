# Architecture: E-commerce Price Monitoring Scraper

## Tech Stack
- **Scraping:** Python with `requests` + `BeautifulSoup` for static sites; `Playwright` or `Selenium` for JavaScript-rendered sites
- **Scheduling:** n8n (cron-based trigger) or a simple cron job / Airflow DAG for daily runs
- **Data cleaning:** pandas — normalize currency formats, strip promotional text, standardize product identifiers
- **Storage:** PostgreSQL for structured price history; each row = product, competitor, price, currency, availability, timestamp
- **Alerting:** n8n workflow or Python script sending email/Slack notifications on threshold-based price changes
- **Reporting:** CSV export or a lightweight dashboard (Streamlit or Power BI, reusing the dashboard pattern from Project 3) for visualization

## Data Flow
1. Scheduler triggers the scraper on a defined interval (e.g. daily at 6 AM)
2. Scraper visits each configured product URL and extracts price, availability, and product title
3. Raw scraped data is cleaned: currency symbols stripped, prices converted to a consistent numeric format, missing/failed scrapes flagged
4. Cleaned data is compared against the most recent stored price for that product/competitor
5. If the price has changed beyond a configured threshold (e.g. ±5%), an alert is triggered
6. New price record is appended to the historical database
7. Reporting layer queries the database to produce the comparison report/dashboard

## Components
| Component | Responsibility |
|---|---|
| Scheduler | Triggers scraping runs on schedule |
| Scraper Engine | Extracts raw price/product data per site |
| Cleaning Module | Normalizes and validates scraped data |
| Change Detection | Compares new vs. historical prices, flags significant changes |
| Alert Service | Sends notifications on price changes |
| Database | Stores structured price history |
| Reporting Layer | Generates comparison exports/dashboards |

## Non-Functional Considerations
- **Resilience:** Scraper should log and gracefully skip failed URLs (site down, structure changed) rather than crashing the whole run
- **Rate limiting:** Requests should be throttled and randomized (delays, user-agent rotation) to avoid overloading target sites or triggering blocks
- **Maintainability:** Each site's scraping logic should be modular (one scraper module per site) so a single site's redesign doesn't break the others
