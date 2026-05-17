# Models

All core tables use Integer primary keys with autoincrement for simpler joins and SQLite compatibility in tests.
Foreign keys reference the integer IDs across stores, skus, sales_logs, forecasts, and reorder_suggestions.
