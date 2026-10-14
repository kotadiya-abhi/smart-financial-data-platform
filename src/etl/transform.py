"""Transforms validated string-typed rows into real Python types ready for
the database (dates become date objects, amounts become floats)."""

import pandas as pd


def transform_customers(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["signup_date"] = pd.to_datetime(out["signup_date"], format="%Y-%m-%d").dt.date
    return out


def transform_transactions(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["transaction_date"] = pd.to_datetime(out["transaction_date"], format="%Y-%m-%d").dt.date
    out["amount"] = out["amount"].astype(float)
    return out
