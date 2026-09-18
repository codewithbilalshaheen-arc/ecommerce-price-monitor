import argparse
import sys
from pathlib import Path

# Ensure project root directory is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from src.db.session import init_db, get_db
from src.db.seed import seed_demo_data
from src.db.models import Product, PriceLog, AlertLog, CompetitorUrl
from src.scraper.engine import ScrapingEngine


def run_scrape(use_playwright: bool = False, threshold_pct: float = 5.0):
    """Run scraper for all tracked competitor URLs."""
    print("Starting price scraper run...")
    engine = ScrapingEngine(use_playwright=use_playwright)
    results = engine.run_all(threshold_pct=threshold_pct)
    print(f"Scrape completed! {len(results)} prices successfully updated.")


def export_report(output_file: str = "data/price_report.csv"):
    """Export current and historical price data to CSV report."""
    with get_db() as db:
        logs = (
            db.query(PriceLog, Product.name, CompetitorUrl.competitor_name)
            .join(Product, PriceLog.product_id == Product.id)
            .join(CompetitorUrl, PriceLog.competitor_url_id == CompetitorUrl.id)
            .order_by(PriceLog.scraped_at.desc())
            .all()
        )

        data = []
        for log, product_name, comp_name in logs:
            data.append({
                "Log ID": log.id,
                "Product": product_name,
                "Competitor": comp_name,
                "Price": log.price,
                "Currency": log.currency,
                "Available": log.is_available,
                "Scraped At": log.scraped_at.strftime("%Y-%m-%d %H:%M:%S") if log.scraped_at else "",
            })

        df = pd.DataFrame(data)
        df.to_csv(output_file, index=False)
        print(f"Exported price report with {len(df)} records to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="E-commerce Price Monitoring Scraper CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init-db
    subparsers.add_parser("init-db", help="Initialize database schema")

    # seed
    subparsers.add_parser("seed", help="Seed database with demo products and historical data")

    # scrape
    scrape_parser = subparsers.add_parser("scrape", help="Run scheduled price scraping job")
    scrape_parser.add_argument("--playwright", action="store_true", help="Use Playwright for dynamic rendering")
    scrape_parser.add_argument("--threshold", type=float, default=5.0, help="Alert threshold percentage")

    # export
    export_parser = subparsers.add_parser("export", help="Export price history to CSV")
    export_parser.add_argument("--output", type=str, default="data/price_report.csv", help="CSV output path")

    args = parser.parse_args()

    if args.command == "init-db":
        init_db()
        print("Database initialized successfully.")
    elif args.command == "seed":
        seed_demo_data()
    elif args.command == "scrape":
        run_scrape(use_playwright=args.playwright, threshold_pct=args.threshold)
    elif args.command == "export":
        export_report(args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
