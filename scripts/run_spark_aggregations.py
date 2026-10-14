"""Phase 3 entry point: pull transactions from Postgres, aggregate them
with PySpark (by region, date, customer, type), and save the results.

Windows note: Spark's native Parquet writer needs a Hadoop utility
(winutils.exe) that isn't installed here, and that we'd rather not pull
in as an unofficial third-party binary just for this. Since the
aggregated outputs are small (a handful to a few hundred rows each),
we collect them back to the driver and write Parquet via pandas/pyarrow
instead -- the actual grouping/aggregation work still happens in Spark,
which is the point of this phase.
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

import pandas as pd
from pyspark.sql import SparkSession

from src.etl.load import load_daily_analytics
from src.spark_jobs import aggregations
from src.utils.db import get_connection

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def main() -> None:
    conn = get_connection()
    transactions_pd = pd.read_sql("SELECT * FROM transactions", conn)
    print(f"Pulled {len(transactions_pd)} transactions from Postgres")

    spark = SparkSession.builder.appName("smart-financial-aggregations").master("local[*]").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    transactions_spark = spark.createDataFrame(transactions_pd)
    transactions_spark.cache()

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    results = {
        "by_region": aggregations.by_region(transactions_spark),
        "by_date": aggregations.by_date(transactions_spark),
        "by_customer": aggregations.by_customer(transactions_spark),
        "by_transaction_type": aggregations.by_transaction_type(transactions_spark),
        "by_date_and_region": aggregations.by_date_and_region(transactions_spark),
    }

    for name, spark_df in results.items():
        pandas_df = spark_df.toPandas()
        out_path = PROCESSED_DIR / f"{name}.parquet"
        pandas_df.to_parquet(out_path, index=False)
        print(f"{name}: {len(pandas_df)} rows -> {out_path.name}")

    daily_region_pd = results["by_date_and_region"].toPandas()
    daily_region_pd = daily_region_pd.rename(columns={"transaction_date": "analytics_date"})
    loaded = load_daily_analytics(conn, daily_region_pd)
    print(f"Upserted {loaded} rows into daily_analytics")

    spark.stop()
    conn.close()
    print("Phase 3 aggregation run finished successfully")


if __name__ == "__main__":
    main()
