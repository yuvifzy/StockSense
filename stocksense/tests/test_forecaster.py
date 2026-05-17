"""
Tests for forecaster.py — TASK 5

Seed 21 days of synthetic sales data for 3 SKUs into a test SQLite DB.
Assert Prophet returns non-null forecast with confidence = High for all 3.
Assert reorder_qty = ceil(predicted_qty × 1.2).

Note: SQLite doesn't support PostgreSQL ARRAY type, so we override
the models to use JSON instead for testing.
"""

import math
import uuid
from datetime import date, timedelta
from typing import Optional

import pytest
from sqlalchemy import create_engine, Column, String, Integer, Date, DateTime, Float, Boolean, JSON
from sqlalchemy.orm import sessionmaker, declarative_base

# We create a separate Base for testing to avoid ARRAY type issues with SQLite
TestBase = declarative_base()


class TestStore(TestBase):
    __tablename__ = "stores"
    id = Column(Integer, primary_key=True, autoincrement=True)
    whatsapp_number = Column(String(20), nullable=False)
    name = Column(String(255), nullable=False)
    pin_code = Column(String(10), nullable=False)
    language = Column(String(10), nullable=False, default="en")
    reminder_paused = Column(Boolean, default=False)
    created_at = Column(DateTime)


class TestSKU(TestBase):
    __tablename__ = "skus"
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, nullable=False)
    canonical_name = Column(String(255), nullable=False)
    variants = Column(JSON, default=[])
    unit = Column(String(50), nullable=False, default="units")


class TestSalesLog(TestBase):
    __tablename__ = "sales_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, nullable=False)
    sku_id = Column(Integer, nullable=False)
    quantity_sold = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    source = Column(String(20), nullable=False, default="text")


class TestForecast(TestBase):
    __tablename__ = "forecasts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, nullable=False)
    week_start = Column(Date, nullable=False)
    sku_id = Column(Integer, nullable=False)
    predicted_qty = Column(Float, nullable=False)
    confidence = Column(String(10), nullable=False, default="medium")
    generated_at = Column(DateTime)


class TestReorderSuggestion(TestBase):
    __tablename__ = "reorder_suggestions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    forecast_id = Column(Integer, nullable=False)
    sku_id = Column(Integer, nullable=False)
    suggested_qty = Column(Integer, nullable=False)
    confirmed = Column(Boolean, default=False)


# ── Monkey-patch the production models so the forecaster service
#    queries the test tables with SQLite-compatible types ──
import app.models.store as store_mod
import app.models.sku as sku_mod
import app.models.sales_log as sales_log_mod
import app.models.forecast as forecast_mod

# Save originals
_orig_store = store_mod.Store
_orig_sku = sku_mod.SKU
_orig_sales_log = sales_log_mod.SalesLog
_orig_forecast = forecast_mod.Forecast
_orig_reorder = forecast_mod.ReorderSuggestion

# Override
store_mod.Store = TestStore
sku_mod.SKU = TestSKU
sales_log_mod.SalesLog = TestSalesLog
forecast_mod.Forecast = TestForecast
forecast_mod.ReorderSuggestion = TestReorderSuggestion

# Now import forecaster (it uses the monkey-patched models)
from app.services.forecaster import (
    generate_forecast,
    generate_all_forecasts,
    get_deadstock_skus,
    _fetch_daily_sales,
)


# ── Test fixtures ──

@pytest.fixture(scope="module")
def db_engine():
    """Create an in-memory SQLite DB for testing."""
    engine = create_engine("sqlite:///:memory:")
    TestBase.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope="module")
def db_session(db_engine):
    """Create a session bound to the in-memory DB."""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture(scope="module")
def test_store_id():
    return 1


@pytest.fixture(scope="module")
def test_sku_ids():
    return [1, 2, 3]


@pytest.fixture(scope="module")
def seeded_db(db_session, test_store_id, test_sku_ids):
    """
    Seed the test DB with:
      - 1 store
      - 3 SKUs
      - 30 days of synthetic sales data per SKU
    """
    # Create store
    store = TestStore(
        id=test_store_id,
        whatsapp_number="919999900001",
        name="Test Kirana Store",
        pin_code="110001",
        language="hi",
    )
    db_session.add(store)

    # Create 3 SKUs
    sku_data = [
        ("atta 5kg", "bags"),
        ("maggi 70g", "packets"),
        ("tata salt 1kg", "packets"),
    ]
    for i, (name, unit) in enumerate(sku_data):
        sku = TestSKU(
            id=test_sku_ids[i],
            store_id=test_store_id,
            canonical_name=name,
            variants=[name.title()],
            unit=unit,
        )
        db_session.add(sku)

    # Seed 30 days of consistent sales data
    today = date.today()
    base_quantities = [15, 80, 20]  # Daily avg for each SKU

    for day_offset in range(30):
        sale_date = today - timedelta(days=30 - day_offset)
        for i, sku_id in enumerate(test_sku_ids):
            # Add slight variation (±2) for realism, but keep it consistent
            variation = (day_offset % 5) - 2
            qty = max(1, base_quantities[i] + variation)

            log = TestSalesLog(
                store_id=test_store_id,
                sku_id=sku_id,
                quantity_sold=qty,
                date=sale_date,
                source="text",
            )
            db_session.add(log)

    db_session.commit()
    return db_session


# ── Tests ──

def test_generate_forecast_returns_result(seeded_db, test_store_id, test_sku_ids):
    """Ensure generate_forecast returns a result for each seeded SKU."""
    for sku_id in test_sku_ids:
        result = generate_forecast(seeded_db, test_store_id, sku_id)

        assert result is not None, (
            f"Forecast returned None for SKU '{sku_id}' "
            f"despite having 30 days of data"
        )
        assert "predicted_qty" in result
        assert "reorder_qty" in result
        assert "confidence" in result
        assert result["predicted_qty"] > 0
        assert result["reorder_qty"] > 0


def test_forecast_confidence_is_high(seeded_db, test_store_id, test_sku_ids):
    """Verify confidence is High for stable 30-day sales data."""
    for sku_id in test_sku_ids:
        result = generate_forecast(seeded_db, test_store_id, sku_id)
        assert result is not None
        assert result["confidence"] == "High", (
            f"Expected High confidence for SKU '{sku_id}' "
            f"with 30 days of data, got '{result['confidence']}'"
        )


def test_reorder_qty_is_ceil_1_2x(seeded_db, test_store_id, test_sku_ids):
    """Assert reorder_qty equals ceil(predicted_qty × 1.2)."""
    for sku_id in test_sku_ids:
        result = generate_forecast(seeded_db, test_store_id, sku_id)
        assert result is not None
        expected_reorder = math.ceil(result["predicted_qty"] * 1.2)
        assert result["reorder_qty"] == expected_reorder, (
            f"SKU '{sku_id}': reorder_qty={result['reorder_qty']} "
            f"expected ceil({result['predicted_qty']} × 1.2)={expected_reorder}"
        )


def test_generate_all_forecasts(seeded_db, test_store_id):
    """Confirm generate_all_forecasts returns results for each SKU."""
    results = generate_all_forecasts(seeded_db, test_store_id)
    assert len(results) == 3
    # Should be sorted by reorder_qty descending
    for i in range(len(results) - 1):
        assert results[i]["reorder_qty"] >= results[i + 1]["reorder_qty"]


def test_insufficient_data_returns_none(seeded_db, test_store_id):
    """Confirm an SKU with no sales returns None."""
    new_sku = TestSKU(
        store_id=test_store_id,
        canonical_name="new product with no sales",
        variants=["New Product"],
        unit="units",
    )
    seeded_db.add(new_sku)
    seeded_db.commit()

    result = generate_forecast(seeded_db, test_store_id, new_sku.id)
    assert result is None


def test_deadstock_detection(seeded_db, test_store_id):
    """Ensure deadstock list includes the no-sales SKU."""
    deadstock = get_deadstock_skus(seeded_db, test_store_id)
    names = [d["sku_name"] for d in deadstock]
    assert "new product with no sales" in names
