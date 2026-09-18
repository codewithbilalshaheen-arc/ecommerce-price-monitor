import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.models import Base, Product, CompetitorUrl, PriceLog, AlertLog
from src.analytics.change_detector import detect_price_change_and_alert


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_price_change_detection_triggers_alert(db_session):
    product = Product(name="Test Item")
    db_session.add(product)
    db_session.commit()

    comp = CompetitorUrl(product_id=product.id, competitor_name="Store 1", url="https://store1.com")
    db_session.add(comp)
    db_session.commit()

    # Initial price: $100.00
    log1 = PriceLog(product_id=product.id, competitor_url_id=comp.id, price=100.00)
    db_session.add(log1)
    db_session.commit()

    # New price: $90.00 (10% drop, > 5% threshold)
    log2 = PriceLog(product_id=product.id, competitor_url_id=comp.id, price=90.00)
    db_session.add(log2)
    db_session.commit()

    alert = detect_price_change_and_alert(db_session, comp, log2, threshold_pct=5.0)

    assert alert is not None
    assert alert.alert_type == "PRICE_DROP"
    assert alert.pct_change == -10.0
    assert alert.old_price == 100.00
    assert alert.new_price == 90.00


def test_price_change_below_threshold_does_not_alert(db_session):
    product = Product(name="Test Item 2")
    db_session.add(product)
    db_session.commit()

    comp = CompetitorUrl(product_id=product.id, competitor_name="Store 2", url="https://store2.com")
    db_session.add(comp)
    db_session.commit()

    # Initial price: $100.00
    log1 = PriceLog(product_id=product.id, competitor_url_id=comp.id, price=100.00)
    db_session.add(log1)
    db_session.commit()

    # New price: $98.00 (2% drop, < 5% threshold)
    log2 = PriceLog(product_id=product.id, competitor_url_id=comp.id, price=98.00)
    db_session.add(log2)
    db_session.commit()

    alert = detect_price_change_and_alert(db_session, comp, log2, threshold_pct=5.0)

    assert alert is None
