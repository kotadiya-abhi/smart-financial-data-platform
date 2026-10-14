"""Generates synthetic customers.csv and transactions.csv into data/raw/.

A small percentage of transaction rows are deliberately corrupted (missing
fields, duplicate IDs, invalid amounts, bad dates) so Phase 2 validation
has real problems to catch.
"""

import argparse
import csv
import random
from datetime import date, timedelta
from pathlib import Path

from faker import Faker

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

REGIONS = ["North", "South", "East", "West", "Central"]

# transaction_type -> direction (money coming into vs leaving the customer's account)
TRANSACTION_TYPES = {
    "purchase": "outgoing",
    "bill_payment": "outgoing",
    "withdrawal": "outgoing",
    "transfer": "outgoing",
    "deposit": "incoming",
    "refund": "incoming",
}


def generate_customers(fake: Faker, num_customers: int) -> list[dict]:
    customers = []
    for i in range(1, num_customers + 1):
        signup_date = fake.date_between(start_date="-3y", end_date="-30d")
        customers.append(
            {
                "customer_id": f"CUST{i:05d}",
                "name": fake.name(),
                "region": random.choice(REGIONS),
                "signup_date": signup_date.isoformat(),
            }
        )
    return customers


def random_amount(transaction_type: str) -> float:
    # lognormal gives mostly small/medium amounts with a realistic long tail
    # of occasional large ones -- useful later for anomaly detection.
    base = random.lognormvariate(mu=4.0, sigma=1.0)
    if transaction_type in ("deposit", "transfer"):
        base *= random.uniform(1.0, 3.0)
    return round(base, 2)


def random_date_in_last_year() -> date:
    days_back = random.randint(0, 365)
    return date.today() - timedelta(days=days_back)


def generate_transactions(fake: Faker, customers: list[dict], num_transactions: int) -> list[dict]:
    customer_ids = [c["customer_id"] for c in customers]
    transactions = []
    for i in range(1, num_transactions + 1):
        transaction_type = random.choice(list(TRANSACTION_TYPES))
        transactions.append(
            {
                "transaction_id": f"TXN{i:07d}",
                "customer_id": random.choice(customer_ids),
                "transaction_date": random_date_in_last_year().isoformat(),
                "amount": random_amount(transaction_type),
                "direction": TRANSACTION_TYPES[transaction_type],
                "transaction_type": transaction_type,
                "region": random.choice(REGIONS),
            }
        )
    return transactions


def inject_dirty_rows(transactions: list[dict], dirty_rate: float) -> list[dict]:
    num_dirty = int(len(transactions) * dirty_rate)
    dirty_indexes = random.sample(range(len(transactions)), num_dirty)
    problem_types = ["missing_field", "duplicate_id", "invalid_amount", "bad_date"]

    for idx in dirty_indexes:
        problem = random.choice(problem_types)
        row = transactions[idx]

        if problem == "missing_field":
            field = random.choice(["customer_id", "amount", "transaction_date"])
            row[field] = ""
        elif problem == "duplicate_id":
            other_idx = random.choice([j for j in range(len(transactions)) if j != idx])
            row["transaction_id"] = transactions[other_idx]["transaction_id"]
        elif problem == "invalid_amount":
            row["amount"] = random.choice(["abc", -999.99, "N/A"])
        elif problem == "bad_date":
            row["transaction_date"] = random.choice(["2024-13-45", "not_a_date", "31/02/2024"])

    return transactions


def write_csv(rows: list[dict], path: Path, fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic financial transaction data")
    parser.add_argument("--num-customers", type=int, default=200)
    parser.add_argument("--num-transactions", type=int, default=5000)
    parser.add_argument("--dirty-rate", type=float, default=0.03, help="fraction of transactions to corrupt")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)
    fake = Faker()
    Faker.seed(args.seed)

    customers = generate_customers(fake, args.num_customers)
    transactions = generate_transactions(fake, customers, args.num_transactions)
    transactions = inject_dirty_rows(transactions, args.dirty_rate)

    write_csv(customers, RAW_DIR / "customers.csv", list(customers[0].keys()))
    write_csv(transactions, RAW_DIR / "transactions.csv", list(transactions[0].keys()))

    num_dirty = int(len(transactions) * args.dirty_rate)
    print(f"Generated {len(customers)} customers -> {RAW_DIR / 'customers.csv'}")
    print(f"Generated {len(transactions)} transactions -> {RAW_DIR / 'transactions.csv'}")
    print(f"  ({num_dirty} rows deliberately corrupted for validation testing)")


if __name__ == "__main__":
    main()
