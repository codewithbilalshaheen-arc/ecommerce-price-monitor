import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timezone

from src.db.session import init_db, get_db
from src.db.models import Product, CompetitorUrl, PriceLog, AlertLog
from src.scraper.engine import ScrapingEngine
from src.analytics.alerts import send_slack_notification, send_email_notification
from src.config import EXCHANGE_RATES, convert_and_format_price

st.set_page_config(
    page_title="E-Commerce Price Monitor",
    page_icon="🏷️",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()


def main():
    st.sidebar.title("🏷️ Price Monitor")
    st.sidebar.markdown("---")

    # Global Currency Selection
    selected_currency = st.sidebar.selectbox(
        "💱 Display Currency",
        options=list(EXCHANGE_RATES.keys()),
        index=0,
        help="Select currency to convert and format all price displays across the app."
    )

    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Navigation",
        [
            "📊 Price Comparison",
            "📈 Price History & Trends",
            "🔍 Product Search & Configuration",
            "🔔 Alerts & Settings"
        ]
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("Quick Actions")
    if st.sidebar.button("🔄 Trigger Scrape Job"):
        with st.spinner("Scraping all active competitor URLs..."):
            engine = ScrapingEngine()
            results = engine.run_all()
            st.sidebar.success(f"Scraped {len(results)} active URLs!")
            st.rerun()

    if page == "📊 Price Comparison":
        render_price_comparison(selected_currency)
    elif page == "📈 Price History & Trends":
        render_price_history(selected_currency)
    elif page == "🔍 Product Search & Configuration":
        render_product_search_and_config(selected_currency)
    elif page == "🔔 Alerts & Settings":
        render_alerts_settings(selected_currency)


def render_price_comparison(selected_currency: str):
    st.title("📊 Price Comparison Dashboard")
    st.markdown("Real-time competitor price positioning across tracked products.")

    with get_db() as db:
        products = db.query(Product).all()

        if not products:
            st.warning("No products found in the database. Go to '🔍 Product Search & Configuration' to add products or populate demo data.")
            return

        # Category Filter
        categories = sorted(list({p.category for p in products if p.category}))
        selected_category = st.selectbox(
            "📁 Filter by Category",
            options=["All Categories"] + categories
        )

        if selected_category != "All Categories":
            products = [p for p in products if p.category == selected_category]

        total_products = len(products)
        total_urls = db.query(CompetitorUrl).filter(CompetitorUrl.is_active == True).count()
        recent_alerts_count = db.query(AlertLog).count()

        col1, col2, col3 = st.columns(3)
        col1.metric("Tracked Products", total_products)
        col2.metric("Active Competitor URLs", total_urls)
        col3.metric("Total Alerts Triggered", recent_alerts_count)

        st.markdown("---")

        for prod in products:
            st.subheader(f"📦 {prod.name} (Category: {prod.category or 'General'})")

            comp_urls = db.query(CompetitorUrl).filter(CompetitorUrl.product_id == prod.id, CompetitorUrl.is_active == True).all()

            comp_rows = []
            our_price = None

            for cu in comp_urls:
                latest_log = (
                    db.query(PriceLog)
                    .filter(PriceLog.competitor_url_id == cu.id)
                    .order_by(PriceLog.scraped_at.desc())
                    .first()
                )
                p_val = latest_log.price if latest_log else None
                if cu.is_our_store and p_val:
                    our_price = p_val

                comp_rows.append({
                    "Competitor": cu.competitor_name,
                    "Is Our Store": cu.is_our_store,
                    "Price": p_val,
                    "Last Scraped": latest_log.scraped_at.strftime("%Y-%m-%d %H:%M") if latest_log else "Never",
                    "Status": cu.last_status,
                    "URL": cu.url,
                })

            if not comp_rows:
                st.info("No competitor URLs configured for this product.")
                continue

            df_comp = pd.DataFrame(comp_rows)
            valid_prices = df_comp.dropna(subset=["Price"]).sort_values("Price")

            if not valid_prices.empty:
                lowest_p = valid_prices["Price"].min()
                highest_p = valid_prices["Price"].max()
                lowest_comp = valid_prices.iloc[0]["Competitor"]
                highest_comp = valid_prices.sort_values("Price", ascending=False).iloc[0]["Competitor"]

                m1, m2, m3 = st.columns(3)
                m1.metric("Lowest Price Across Websites", convert_and_format_price(lowest_p, selected_currency), delta=f"Store: {lowest_comp}")
                m2.metric("Highest Price Across Websites", convert_and_format_price(highest_p, selected_currency), delta=f"Store: {highest_comp}")
                m3.metric("Price Spread", convert_and_format_price(highest_p - lowest_p, selected_currency))

            if our_price and not valid_prices.empty:
                lowest_p = valid_prices["Price"].min()
                our_p_fmt = convert_and_format_price(our_price, selected_currency)
                lowest_p_fmt = convert_and_format_price(lowest_p, selected_currency)
                if our_price <= lowest_p:
                    st.success(f"🏆 Best Price Position! Our Price ({our_p_fmt}) is the lowest.")
                else:
                    diff = our_price - lowest_p
                    diff_fmt = convert_and_format_price(diff, selected_currency)
                    st.warning(f"⚠️ Price Attention: Our Price ({our_p_fmt}) is {diff_fmt} higher than lowest competitor ({lowest_p_fmt}).")

            display_data = []
            for row in comp_rows:
                p = row["Price"]
                if p is None:
                    p_str = "N/A"
                    diff_str = "N/A"
                else:
                    p_str = convert_and_format_price(p, selected_currency)
                    if our_price and not row["Is Our Store"]:
                        diff = p - our_price
                        diff_pct = (diff / our_price) * 100
                        diff_val_fmt = convert_and_format_price(abs(diff), selected_currency)
                        if diff < 0:
                            diff_str = f"🔴 {diff_val_fmt} cheaper ({abs(diff_pct):.1f}%)"
                        elif diff > 0:
                            diff_str = f"🟢 {diff_val_fmt} pricier (+{diff_pct:.1f}%)"
                        else:
                            diff_str = "⚪ Same Price"
                    else:
                        diff_str = "--- (Our Price)" if row["Is Our Store"] else "N/A"

                display_data.append({
                    "Store / Competitor": f"⭐ {row['Competitor']}" if row["Is Our Store"] else row["Competitor"],
                    "Current Price": p_str,
                    "vs. Our Store": diff_str,
                    "Last Updated": row["Last Scraped"],
                    "Status": "✅ OK" if row["Status"] == "SUCCESS" else f"❌ {row['Status']}",
                })

            st.table(pd.DataFrame(display_data))
            st.markdown("---")


def render_price_history(selected_currency: str):
    st.title("📈 Price History & Trends")

    with get_db() as db:
        products = db.query(Product).all()
        if not products:
            st.info("No products available.")
            return

        prod_names = {p.id: p.name for p in products}
        selected_prod_id = st.selectbox("Select Product to View History", options=list(prod_names.keys()), format_func=lambda x: prod_names[x])

        logs = (
            db.query(PriceLog, CompetitorUrl.competitor_name, CompetitorUrl.is_our_store)
            .join(CompetitorUrl, PriceLog.competitor_url_id == CompetitorUrl.id)
            .filter(PriceLog.product_id == selected_prod_id)
            .order_by(PriceLog.scraped_at.asc())
            .all()
        )

        if not logs:
            st.info("No price logs recorded yet for this product.")
            return

        rate = EXCHANGE_RATES.get(selected_currency, EXCHANGE_RATES["USD"])["rate"]
        symbol = EXCHANGE_RATES.get(selected_currency, EXCHANGE_RATES["USD"])["symbol"]

        chart_data = []
        for log, comp_name, is_our_store in logs:
            label = f"{comp_name} (Our Store)" if is_our_store else comp_name
            conv_price = round(log.price * rate, 2)
            chart_data.append({
                "Date": log.scraped_at,
                f"Price ({symbol})": conv_price,
                "Competitor": label,
            })

        df_chart = pd.DataFrame(chart_data)

        fig = px.line(
            df_chart,
            x="Date",
            y=f"Price ({symbol})",
            color="Competitor",
            title=f"Price History: {prod_names[selected_prod_id]} ({selected_currency})",
            markers=True,
        )
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📋 Historical Raw Log Entries")
        st.dataframe(df_chart.sort_values("Date", ascending=False), use_container_width=True)

        csv_data = df_chart.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV Report",
            data=csv_data,
            file_name=f"price_history_product_{selected_prod_id}_{selected_currency}.csv",
            mime="text/csv"
        )


def render_product_search_and_config(selected_currency: str):
    st.title("🔍 Product Search & Configuration")

    st.subheader("🔎 Search Specific Product Details Across Websites")
    with get_db() as db:
        products = db.query(Product).all()

        search_query = st.text_input("Enter Product Name or Keyword to Search", value="", placeholder="e.g. Headphones, Watch, Laptop...")
        
        all_categories = sorted(list({p.category for p in products if p.category}))
        selected_cat_scrape = st.selectbox("Or Select Category to Filter / Scrape", options=["All Categories"] + all_categories)

        filtered_prods = products
        if search_query:
            filtered_prods = [p for p in filtered_prods if search_query.lower() in p.name.lower() or search_query.lower() in (p.category or "").lower()]
        if selected_cat_scrape != "All Categories":
            filtered_prods = [p for p in filtered_prods if p.category == selected_cat_scrape]

        if st.button("🚀 Scrape Selected / Filtered Products Now"):
            engine = ScrapingEngine()
            scraped_count = 0
            with st.spinner("Scraping filtered products from websites..."):
                for fp in filtered_prods:
                    curls = db.query(CompetitorUrl).filter(CompetitorUrl.product_id == fp.id, CompetitorUrl.is_active == True).all()
                    for cu in curls:
                        res = engine.run_job_for_url(cu.id)
                        if res:
                            scraped_count += 1
            st.success(f"Scraped {scraped_count} competitor URLs!")
            st.rerun()

        st.markdown("---")
        if filtered_prods:
            st.markdown(f"### Found {len(filtered_prods)} Product(s)")
            for p in filtered_prods:
                with st.expander(f"📦 Product #{p.id}: {p.name} (Category: {p.category or 'General'})", expanded=True):
                    comp_urls = db.query(CompetitorUrl).filter(CompetitorUrl.product_id == p.id, CompetitorUrl.is_active == True).all()
                    prices = []
                    comps_data = []

                    for cu in comp_urls:
                        latest_log = (
                            db.query(PriceLog)
                            .filter(PriceLog.competitor_url_id == cu.id)
                            .order_by(PriceLog.scraped_at.desc())
                            .first()
                        )
                        price_val = latest_log.price if latest_log else None
                        if price_val is not None:
                            prices.append((price_val, cu.competitor_name))

                        comps_data.append({
                            "Competitor": cu.competitor_name,
                            "Our Store": "Yes" if cu.is_our_store else "No",
                            "URL": cu.url,
                            "Price": convert_and_format_price(price_val, selected_currency),
                            "Last Scraped": latest_log.scraped_at.strftime("%Y-%m-%d %H:%M") if latest_log else "Never",
                            "Status": cu.last_status,
                        })

                    if prices:
                        prices.sort(key=lambda x: x[0])
                        lowest_price, lowest_comp = prices[0]
                        highest_price, highest_comp = prices[-1]

                        col1, col2, col3 = st.columns(3)
                        col1.metric("Lowest Price", convert_and_format_price(lowest_price, selected_currency), delta=f"Store: {lowest_comp}")
                        col2.metric("Highest Price", convert_and_format_price(highest_price, selected_currency), delta=f"Store: {highest_comp}")
                        col3.metric("Price Difference", convert_and_format_price(highest_price - lowest_price, selected_currency))

                    st.table(pd.DataFrame(comps_data))
        else:
            st.info("No matching products found. Try adjusting your search query or add a new product below.")

        st.markdown("---")
        st.subheader("➕ Add New Tracked Product")
        with st.form("add_product_form", clear_on_submit=True):
            name = st.text_input("Product Name")
            category = st.text_input("Category", value="General")
            our_url = st.text_input("Our Product Page URL")
            our_price = st.number_input("Our Target / Current Price (in USD $)", min_value=0.0, value=100.0, step=0.01)
            submitted = st.form_submit_button("Add Product")

            if submitted and name:
                new_prod = Product(
                    name=name,
                    category=category,
                    our_url=our_url,
                    target_price=our_price,
                )
                db.add(new_prod)
                db.flush()

                if our_url:
                    our_comp = CompetitorUrl(
                        product_id=new_prod.id,
                        competitor_name="Our Store",
                        is_our_store=True,
                        url=our_url,
                        is_active=True,
                    )
                    db.add(our_comp)

                st.success(f"Added product: {name}")
                st.rerun()

        st.markdown("---")
        st.subheader("🔗 Add Competitor URL to Existing Product")
        if products:
            prod_dict = {p.id: p.name for p in products}
            selected_pid = st.selectbox("Select Target Product", options=list(prod_dict.keys()), format_func=lambda x: prod_dict[x])

            with st.form("add_competitor_form", clear_on_submit=True):
                comp_name = st.text_input("Competitor Name (e.g. Amazon, BestBuy)")
                comp_url = st.text_input("Competitor Product URL")
                price_selector = st.text_input("Custom CSS Selector for Price (optional)", value="")
                title_selector = st.text_input("Custom CSS Selector for Title (optional)", value="")
                comp_submitted = st.form_submit_button("Add Competitor URL")

                if comp_submitted and comp_name and comp_url:
                    new_comp = CompetitorUrl(
                        product_id=selected_pid,
                        competitor_name=comp_name,
                        is_our_store=False,
                        url=comp_url,
                        css_selector_price=price_selector if price_selector else None,
                        css_selector_title=title_selector if title_selector else None,
                        is_active=True,
                    )
                    db.add(new_comp)
                    st.success(f"Added competitor URL for {comp_name}")
                    st.rerun()


def render_alerts_settings(selected_currency: str):
    st.title("🔔 Alerts & Settings")

    st.subheader("⚙️ Alert Threshold Configuration")
    threshold = st.slider("Price Change Alert Threshold (%)", min_value=1.0, max_value=25.0, value=5.0, step=0.5)
    st.info(f"An alert will be triggered whenever a competitor's price changes by **{threshold}%** or more.")

    st.markdown("---")
    st.subheader("🧪 Test Alert Channels")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Test Email Alert"):
            send_email_notification("Test Email Alert", "This is a test notification from E-commerce Price Monitor.")
            st.success("Test email alert logged!")

    with col2:
        if st.button("Test Slack Alert"):
            res = send_slack_notification("🧪 *Test Slack Alert* from E-commerce Price Monitor!")
            if res:
                st.success("Slack alert sent successfully!")
            else:
                st.info("Slack webhook not configured or message logged.")

    st.markdown("---")
    st.subheader("📜 Triggered Alerts Log")

    with get_db() as db:
        alerts = (
            db.query(AlertLog, Product.name, CompetitorUrl.competitor_name)
            .join(Product, AlertLog.product_id == Product.id)
            .join(CompetitorUrl, AlertLog.competitor_url_id == CompetitorUrl.id)
            .order_by(AlertLog.created_at.desc())
            .all()
        )

        if not alerts:
            st.info("No alerts triggered yet.")
            return

        a_data = []
        for alert, prod_name, comp_name in alerts:
            a_data.append({
                "Date": alert.created_at.strftime("%Y-%m-%d %H:%M"),
                "Product": prod_name,
                "Competitor": comp_name,
                "Type": alert.alert_type,
                "Old Price": convert_and_format_price(alert.old_price, selected_currency),
                "New Price": convert_and_format_price(alert.new_price, selected_currency),
                "Change": f"{alert.pct_change:+.2f}%",
                "Message": alert.message,
            })

        st.dataframe(pd.DataFrame(a_data), use_container_width=True)


if __name__ == "__main__":
    main()
