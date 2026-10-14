"""Spark aggregations over the transactions dataset.

Each function takes the raw transactions Spark DataFrame and returns a
grouped summary DataFrame. Kept separate from Pandas/Postgres code so the
aggregation logic itself has no I/O dependencies and stays easy to test.
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def by_region(transactions: DataFrame) -> DataFrame:
    return (
        transactions.groupBy("region")
        .agg(
            F.count("*").alias("transaction_count"),
            F.sum("amount").alias("total_amount"),
        )
        .orderBy("region")
    )


def by_date(transactions: DataFrame) -> DataFrame:
    return (
        transactions.groupBy("transaction_date")
        .agg(
            F.count("*").alias("transaction_count"),
            F.sum(F.when(F.col("direction") == "incoming", F.col("amount")).otherwise(0)).alias("total_incoming"),
            F.sum(F.when(F.col("direction") == "outgoing", F.col("amount")).otherwise(0)).alias("total_outgoing"),
        )
        .orderBy("transaction_date")
    )


def by_customer(transactions: DataFrame) -> DataFrame:
    return (
        transactions.groupBy("customer_id")
        .agg(
            F.count("*").alias("transaction_count"),
            F.sum("amount").alias("total_amount"),
        )
        .orderBy(F.desc("total_amount"))
    )


def by_transaction_type(transactions: DataFrame) -> DataFrame:
    return (
        transactions.groupBy("transaction_type")
        .agg(
            F.count("*").alias("transaction_count"),
            F.sum("amount").alias("total_amount"),
        )
        .orderBy(F.desc("total_amount"))
    )


def by_date_and_region(transactions: DataFrame) -> DataFrame:
    """Matches the shape of the daily_analytics table (date + region grain)."""
    return (
        transactions.groupBy("transaction_date", "region")
        .agg(
            F.count("*").alias("transaction_count"),
            F.sum(F.when(F.col("direction") == "incoming", F.col("amount")).otherwise(0)).alias("total_incoming"),
            F.sum(F.when(F.col("direction") == "outgoing", F.col("amount")).otherwise(0)).alias("total_outgoing"),
        )
        .orderBy("transaction_date", "region")
    )
