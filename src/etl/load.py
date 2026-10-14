"""Loads transformed DataFrames into PostgreSQL.

Uses ON CONFLICT DO NOTHING on the primary key so re-running the pipeline
on the same source file never inserts duplicates.
"""

import pandas as pd
from psycopg2.extras import execute_values


def load_customers(conn, df: pd.DataFrame) -> int:
    if df.empty:
        return 0
    rows = list(df[["customer_id", "name", "region", "signup_date"]].itertuples(index=False, name=None))
    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO customers (customer_id, name, region, signup_date)
            VALUES %s
            ON CONFLICT (customer_id) DO NOTHING
            """,
            rows,
        )
    conn.commit()
    return len(rows)


def load_transactions(conn, df: pd.DataFrame) -> int:
    if df.empty:
        return 0
    columns = ["transaction_id", "customer_id", "transaction_date", "amount", "direction", "transaction_type", "region"]
    rows = list(df[columns].itertuples(index=False, name=None))
    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO transactions
                (transaction_id, customer_id, transaction_date, amount, direction, transaction_type, region)
            VALUES %s
            ON CONFLICT (transaction_id) DO NOTHING
            """,
            rows,
        )
    conn.commit()
    return len(rows)


def load_daily_analytics(conn, df: pd.DataFrame) -> int:
    """Upserts (not skip-on-conflict) because re-running Spark should
    refresh the numbers if the underlying transactions changed."""
    if df.empty:
        return 0
    columns = ["analytics_date", "region", "transaction_count", "total_incoming", "total_outgoing"]
    rows = list(df[columns].itertuples(index=False, name=None))
    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO daily_analytics
                (analytics_date, region, transaction_count, total_incoming, total_outgoing)
            VALUES %s
            ON CONFLICT (analytics_date, region) DO UPDATE SET
                transaction_count = EXCLUDED.transaction_count,
                total_incoming = EXCLUDED.total_incoming,
                total_outgoing = EXCLUDED.total_outgoing
            """,
            rows,
        )
    conn.commit()
    return len(rows)
