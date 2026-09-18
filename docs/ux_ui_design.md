# UX/UI Design: E-commerce Price Monitoring Scraper

## User Flow
1. Business owner logs into the dashboard
2. Adds/edits the list of tracked products (their own product + competitor URLs mapped to it)
3. Views the Price Comparison dashboard showing current standing across competitors
4. Receives email/Slack alerts automatically when a significant price change is detected
5. Drills into a specific product's price history chart to see trends over time

## Key Screens

### 1. Product Configuration Page
- Table: "Our Product" name/URL paired with one or more "Competitor" URLs
- "Add Product to Track" button — simple form (product name, our URL, competitor URL(s))
- Status indicator per row: Active / Scrape Failed (with last successful check timestamp)

### 2. Price Comparison Dashboard
- Table or card view: one row per tracked product
  - Our current price
  - Each competitor's current price, color-coded (green if we're cheaper, red if we're more expensive)
  - "Price position" badge (e.g. "Lowest," "2nd of 4," "Highest")
- Sort/filter by category, by "we're currently priced highest" to prioritize review

### 3. Product Price History Detail
- Line chart: price over time, one line per competitor + our own price, same chart for easy comparison
- Table below: raw price log entries with timestamps
- Export button (CSV) for that product's history

### 4. Alerts / Notification Settings
- List of recent alerts triggered (product, competitor, old price → new price, date)
- Settings: threshold % for triggering an alert, notification channel (email/Slack), notification frequency (immediate vs. daily digest)

## Visual Style Notes
- Price comparison table is the most-used screen — keep it dense but scannable, similar to a spreadsheet but with color-coded visual cues instead of relying on reading every number
- Alerts should feel actionable, not just informational — include a direct link back to the product detail page from each alert
