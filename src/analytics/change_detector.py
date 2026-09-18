import logging
from typing import Optional
from sqlalchemy.orm import Session
from src.db.models import CompetitorUrl, PriceLog, AlertLog
from src.analytics.alerts import send_slack_notification, send_email_notification

logger = logging.getLogger(__name__)


def detect_price_change_and_alert(
    db: Session,
    comp_url: CompetitorUrl,
    new_price_log: PriceLog,
    threshold_pct: float = 5.0,
) -> Optional[AlertLog]:
    previous_log = (
        db.query(PriceLog)
        .filter(
            PriceLog.competitor_url_id == comp_url.id,
            PriceLog.id != new_price_log.id,
        )
        .order_by(PriceLog.scraped_at.desc())
        .first()
    )

    if not previous_log:
        return None

    old_price = previous_log.price
    new_price = new_price_log.price

    if old_price <= 0:
        return None

    pct_change = round(((new_price - old_price) / old_price) * 100, 2)

    if abs(pct_change) >= threshold_pct:
        alert_type = "PRICE_DROP" if pct_change < 0 else "PRICE_INCREASE"
        action_word = "dropped" if pct_change < 0 else "increased"
        msg = (
            f"Alert: Price for '{new_price_log.scraped_title or comp_url.product.name}' "
            f"at {comp_url.competitor_name} {action_word} by {abs(pct_change)}% "
            f"(from ${old_price:.2f} to ${new_price:.2f})."
        )

        alert_log = AlertLog(
            product_id=comp_url.product_id,
            competitor_url_id=comp_url.id,
            old_price=old_price,
            new_price=new_price,
            pct_change=pct_change,
            alert_type=alert_type,
            message=msg,
        )
        db.add(alert_log)
        db.flush()

        send_slack_notification(msg)
        send_email_notification(f"Price Alert: {comp_url.competitor_name}", msg)

        return alert_log

    return None