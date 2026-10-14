"""Reads raw CSV files and checks that the expected columns are present.

This is the "front door" check: before we trust a file's contents at all,
we confirm it has the shape we expect. Row-level problems (bad values,
duplicates) are handled later by the validation step, not here.
"""

import pandas as pd

CUSTOMER_COLUMNS = ["customer_id", "name", "region", "signup_date"]
TRANSACTION_COLUMNS = [
    "transaction_id",
    "customer_id",
    "transaction_date",
    "amount",
    "direction",
    "transaction_type",
    "region",
]


class SchemaError(Exception):
    pass


def _check_columns(df: pd.DataFrame, expected: list[str], file_label: str) -> None:
    missing = set(expected) - set(df.columns)
    if missing:
        raise SchemaError(f"{file_label} is missing required columns: {sorted(missing)}")


def read_customers(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    _check_columns(df, CUSTOMER_COLUMNS, "customers.csv")
    return df


def read_transactions(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    _check_columns(df, TRANSACTION_COLUMNS, "transactions.csv")
    return df
