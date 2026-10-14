"""Row-level validation for customers."""

import pandas as pd


def _is_blank(value: str) -> bool:
    return value is None or str(value).strip() == ""


def validate_customers(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    valid_rows = []
    rejected_rows = []
    seen_customer_ids = set()

    for row in df.to_dict(orient="records"):
        reason = None

        if _is_blank(row["customer_id"]):
            reason = "missing customer_id"
        elif _is_blank(row["name"]):
            reason = "missing name"
        elif row["customer_id"] in seen_customer_ids:
            reason = "duplicate customer_id"
        elif pd.isna(pd.to_datetime(row["signup_date"], format="%Y-%m-%d", errors="coerce")):
            reason = "invalid signup_date"

        if reason:
            rejected_rows.append({**row, "rejection_reason": reason})
        else:
            seen_customer_ids.add(row["customer_id"])
            valid_rows.append(row)

    valid_df = pd.DataFrame(valid_rows, columns=df.columns)
    rejected_df = pd.DataFrame(rejected_rows, columns=[*df.columns, "rejection_reason"])
    return valid_df, rejected_df
