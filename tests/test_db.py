import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.models import Base, Product, CompetitorUrl, PriceLog, AlertLog


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_product_creation(in_memory_db):
    product = Product(name="Test Phone", category="Mobile", target_price=699.99)
    in_memory_db.add(product)
    in_memory_db.commit()

    retrieved = in_memory_db.query(Product).first()
    assert retrieved is not None
    assert retrieved.name == "Test Phone"
    assert retrieved.target_price == 699.99


def test_competitor_url_relationship(in_memory_db):
    product = Product(name="Test Laptop")
    in_memory_db.add(product)
    in_memory_db.commit()

    comp = CompetitorUrl(
        product_id=product.id,
        competitor_name="CompStore",
        url="https://example.com/laptop",
    )
    in_memory_db.add(comp)
    in_memory_db.commit()

    assert len(product.competitor_urls) == 1
    assert product.competitor_urls[0].competitor_name == "CompStore"


def test_price_log_creation(in_memory_db):
    product = Product(name="Tablet")
    in_memory_db.add(product)
    in_memory_db.commit()

    comp = CompetitorUrl(product_id=product.id, competitor_name="StoreA", url="https://a.com")
    in_memory_db.add(comp)
    in_memory_db.commit()

    log = PriceLog(
        product_id=product.id,
        competitor_url_id=comp.id,
        price=399.99,
        currency="USD",
    )
    in_memory_db.add(log)
    in_memory_db.commit()

    assert in_memory_db.query(PriceLog).count() == 1
    assert log.price == 399.99
