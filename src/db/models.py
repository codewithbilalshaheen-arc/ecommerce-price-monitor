from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def utc_now():
    return datetime.now(timezone.utc)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True, default="General")
    our_url = Column(Text, nullable=True)
    target_price = Column(Float, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    competitor_urls = relationship("CompetitorUrl", back_populates="product", cascade="all, delete-orphan")
    price_logs = relationship("PriceLog", back_populates="product", cascade="all, delete-orphan")
    alert_logs = relationship("AlertLog", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}')>"


class CompetitorUrl(Base):
    __tablename__ = "competitor_urls"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    competitor_name = Column(String(100), nullable=False)
    is_our_store = Column(Boolean, default=False)
    url = Column(Text, nullable=False)
    css_selector_price = Column(String(255), nullable=True)
    css_selector_title = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    last_scraped_at = Column(DateTime, nullable=True)
    last_status = Column(String(50), default="PENDING")
    last_error = Column(Text, nullable=True)

    product = relationship("Product", back_populates="competitor_urls")
    price_logs = relationship("PriceLog", back_populates="competitor_url", cascade="all, delete-orphan")
    alert_logs = relationship("AlertLog", back_populates="competitor_url", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CompetitorUrl(id={self.id}, name='{self.competitor_name}', url='{self.url}')>"


class PriceLog(Base):
    __tablename__ = "price_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    competitor_url_id = Column(Integer, ForeignKey("competitor_urls.id", ondelete="CASCADE"), nullable=False)
    scraped_title = Column(String(255), nullable=True)
    raw_price_text = Column(String(100), nullable=True)
    price = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    is_available = Column(Boolean, default=True)
    scraped_at = Column(DateTime, default=utc_now)

    product = relationship("Product", back_populates="price_logs")
    competitor_url = relationship("CompetitorUrl", back_populates="price_logs")

    def __repr__(self):
        return f"<PriceLog(product_id={self.product_id}, price={self.price}, scraped_at='{self.scraped_at}')>"


class AlertLog(Base):
    __tablename__ = "alert_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    competitor_url_id = Column(Integer, ForeignKey("competitor_urls.id", ondelete="CASCADE"), nullable=False)
    old_price = Column(Float, nullable=False)
    new_price = Column(Float, nullable=False)
    pct_change = Column(Float, nullable=False)
    alert_type = Column(String(50), nullable=False)  # e.g., "PRICE_DROP", "PRICE_INCREASE"
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utc_now)

    product = relationship("Product", back_populates="alert_logs")
    competitor_url = relationship("CompetitorUrl", back_populates="alert_logs")

    def __repr__(self):
        return f"<AlertLog(product_id={self.product_id}, pct_change={self.pct_change}%)>"
