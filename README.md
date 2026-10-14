# Smart Financial Data Intelligence Platform

An end-to-end data project that ingests synthetic financial transaction data, validates and transforms it, processes it at scale, surfaces business insights, and flags unusual transactions using machine learning.

Built to demonstrate Data Engineering, Big Data, Data Analytics, and Data Science in a single pipeline.

> This is an educational project using synthetic/anonymized data only — not a production banking or compliance system. Anomaly scores are indicators for review, not confirmed fraud.

## Pipeline

```
Synthetic transaction CSVs
        -> Python ingestion & validation
        -> ETL transformation
        -> PySpark processing & aggregation
        -> PostgreSQL tables + Parquet output
        -> ML anomaly scoring
        -> Power BI dashboard
```

## Tech stack

| Area | Tool |
|---|---|
| Core language | Python |
| Data prep | Pandas |
| Data engineering | Python + SQL |
| Big data | Apache Spark / PySpark |
| Database | PostgreSQL |
| Data science | scikit-learn |
| Dashboard | Power BI |
| Orchestration (optional) | Apache Airflow |

## Project structure

```
data/           synthetic input CSVs, processed output, rejected records (gitignored)
src/
  ingestion/    read & schema-check raw CSVs
  validation/   cleaning & validation rules
  etl/          transform + load into PostgreSQL
  spark_jobs/   PySpark aggregation jobs
  ml/           anomaly detection model
  utils/        shared helpers (db connection, logging)
sql/            database schema
notebooks/      exploration / experiments
dashboards/     Power BI report
tests/          test suite
logs/           pipeline run logs (gitignored)
docs/           architecture notes
```

## Status

Build in progress — see commit history for day-by-day progress.

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
