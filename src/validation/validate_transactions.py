"""Row-level validation for transactions.

Every row is checked against each rule in order; the first rule a row
fails becomes its rejection_reason, and the row is routed to the
rejected set instead of the valid set.
"""

import pandas as pd

VALID_DIRECTIONS = {"incoming", "outgoing"}


def _is_blank(value: str) -> bool:
    return value is None or str(value).strip() == ""


def _parse_amount(value: str) -> float | None:
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return None
    return amount


def _parse_date(value: str) -> pd.Timestamp | None:
    parsed = pd.to_datetime(value, format="%Y-%m-%d", errors="coerce")
    return None if pd.isna(parsed) else parsed


def validate_transactions(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    valid_rows = []
    rejected_rows = []
    seen_transaction_ids = set()

    for row in df.to_dict(orient="records"):
        reason = None

        if _is_blank(row["transaction_id"]):
            reason = "missing transaction_id"
        elif _is_blank(row["customer_id"]):
            reason = "missing customer_id"
        elif _is_blank(row["amount"]):
            reason = "missing amount"
        elif _is_blank(row["transaction_date"]):
            reason = "missing transaction_date"
        elif row["transaction_id"] in seen_transaction_ids:
            reason = "duplicate transaction_id"
        elif _parse_amount(row["amount"]) is None:
            reason = "invalid amount (not numeric)"
        elif _parse_amount(row["amount"]) < 0:
            reason = "invalid amount (negative)"
        elif _parse_date(row["transaction_date"]) is None:
            reason = "invalid transaction_date"
        elif row["direction"] not in VALID_DIRECTIONS:
            reason = "invalid direction"

        if reason:
            rejected_rows.append({**row, "rejection_reason": reason})
        else:
            seen_transaction_ids.add(row["transaction_id"])
            valid_rows.append(row)

    valid_df = pd.DataFrame(valid_rows, columns=df.columns)
    rejected_df = pd.DataFrame(rejected_rows, columns=[*df.columns, "rejection_reason"])
    return valid_df, rejected_df
