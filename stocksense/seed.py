"""Seed script for StockSense dev data."""

import random
from datetime import date, timedelta

from app.database import SessionLocal
from app.models.store import Store
from app.models.sku import SKU
from app.models.sales_log import SalesLog


def main() -> None:
    db = SessionLocal()
    try:
        store = Store(
            whatsapp_number="919999999999",
            name="Sharma Kirana",
            pin_code="110017",
            language="hi",
        )
        db.add(store)
        db.flush()

        sku_specs = [
            ("Toor Dal 1kg", "bag"),
            ("Maggi 70g", "packet"),
            ("Parle-G 800g", "packet"),
            ("Amul Butter 500g", "piece"),
            ("Surf Excel 1kg", "packet"),
        ]

        skus = []
        for name, unit in sku_specs:
            sku = SKU(
                store_id=store.id,
                canonical_name=name,
                variants=[name],
                unit=unit,
            )
            db.add(sku)
            skus.append(sku)

        db.flush()

        start_date = date.today() - timedelta(days=29)
        for day_offset in range(30):
            sale_date = start_date + timedelta(days=day_offset)
            for sku in skus:
                qty = random.randint(2, 8)
                db.add(
                    SalesLog(
                        store_id=store.id,
                        sku_id=sku.id,
                        quantity_sold=qty,
                        date=sale_date,
                        source="text",
                    )
                )

        db.commit()
        print(
            f"Seeded store id={store.id} with 5 SKUs and 30 days of sales"
        )
        print("\nSeed summary")
        print(f"{'Stores':<14}1")
        print(f"{'SKUs':<14}{len(skus)}")
        print(f"{'Sales logs':<14}{len(skus) * 30}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
