"""Phase 2 entry point: ingest, validate, transform, and load the raw CSVs
into PostgreSQL, writing rejected rows to data/rejected/ and logging the
run to pipeline_logs.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.etl.load import load_customers, load_transactions
from src.etl.pipeline_log import finish_run, start_run
from src.etl.transform import transform_customers, transform_transactions
from src.ingestion.read_csv import read_customers, read_transactions
from src.utils.db import get_connection
from src.validation.validate_customers import validate_customers
from src.validation.validate_transactions import validate_transactions

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
REJECTED_DIR = Path(__file__).resolve().parent.parent / "data" / "rejected"


def main() -> None:
    conn = get_connection()
    run_id = start_run(conn)
    print(f"Pipeline run {run_id} started")

    try:
        customers_raw = read_customers(RAW_DIR / "customers.csv")
        transactions_raw = read_transactions(RAW_DIR / "transactions.csv")

        valid_customers, rejected_customers = validate_customers(customers_raw)
        valid_transactions, rejected_transactions = validate_transactions(transactions_raw)

        REJECTED_DIR.mkdir(parents=True, exist_ok=True)
        rejected_customers.to_csv(REJECTED_DIR / "customers_rejected.csv", index=False)
        rejected_transactions.to_csv(REJECTED_DIR / "transactions_rejected.csv", index=False)

        clean_customers = transform_customers(valid_customers)
        clean_transactions = transform_transactions(valid_transactions)

        customers_loaded = load_customers(conn, clean_customers)
        transactions_loaded = load_transactions(conn, clean_transactions)

        total_processed = customers_loaded + transactions_loaded
        total_rejected = len(rejected_customers) + len(rejected_transactions)

        finish_run(conn, run_id, status="success", records_processed=total_processed, records_rejected=total_rejected)

        print(f"Customers: {customers_loaded} loaded, {len(rejected_customers)} rejected")
        print(f"Transactions: {transactions_loaded} loaded, {len(rejected_transactions)} rejected")
        print(f"Pipeline run {run_id} finished successfully")

    except Exception as exc:
        finish_run(conn, run_id, status="failed", records_processed=0, records_rejected=0, error_details=str(exc))
        print(f"Pipeline run {run_id} FAILED: {exc}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
