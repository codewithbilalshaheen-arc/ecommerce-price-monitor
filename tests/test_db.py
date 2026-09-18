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


def test_init_db_concurrency_and_existing_tables(monkeypatch, tmp_path):
    import threading
    from sqlalchemy.exc import OperationalError
    from src.db.session import init_db

    db_file = tmp_path / "test_init.db"
    test_db_url = f"sqlite:///{db_file}"
    monkeypatch.setattr("src.db.session.DATABASE_URL", test_db_url)
    from src.db import session
    test_engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    monkeypatch.setattr(session, "engine", test_engine)

    # Calling init_db multiple times / concurrently should not raise errors even if tables exist
    exceptions = []

    def worker():
        try:
            init_db()
        except Exception as e:
            exceptions.append(e)

    threads = [threading.Thread(target=worker) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not exceptions, f"Exceptions occurred during init_db: {exceptions}"

    # Test OperationalError with 'already exists' is caught, but other OperationalErrors are re-raised
    def raise_other_op_error(*args, **kwargs):
        raise OperationalError("SELECT 1", {}, Exception("database is locked"))

    monkeypatch.setattr(Base.metadata, "create_all", raise_other_op_error)
    with pytest.raises(OperationalError) as exc_info:
        init_db()
    assert "database is locked" in str(exc_info.value)
