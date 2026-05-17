import sys
sys.path.insert(0, '.')

from app.database import SessionLocal
from app.models.store import Store
from app.models.sku import SKU
from app.models.sales_log import SalesLog
from datetime import datetime, timedelta
import random

db = SessionLocal()

existing = db.query(Store).filter(Store.name == "Sharma Kirana").first()
if existing:
    print("Already seeded")
    db.close()
    raise SystemExit(0)

store = Store(name="Sharma Kirana", pin_code="110017", language="hi")
db.add(store)
db.commit()
db.refresh(store)

skus_data = [
    ("Toor Dal 1kg", "bag"),
    ("Maggi 70g", "packet"),
    ("Parle-G 800g", "packet"),
    ("Amul Butter 500g", "piece"),
    ("Surf Excel 1kg", "packet"),
]

skus = []
for name, unit in skus_data:
    sku = SKU(store_id=store.id, canonical_name=name, unit=unit)
    db.add(sku)
    skus.append(sku)
db.commit()

for sku in skus:
    db.refresh(sku)
    for day in range(30):
        log = SalesLog(
            store_id=store.id,
            sku_id=sku.id,
            quantity_sold=random.randint(2, 8),
            date=datetime.now().date() - timedelta(days=day)
        )
        db.add(log)
db.commit()
store_id = store.id
db.close()
print(f"Seeded store id={store_id} with 5 SKUs and 30 days of sales")
