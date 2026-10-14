"""Single place that knows how to connect to PostgreSQL.

Connection settings are read from environment variables (loaded from .env),
never hardcoded, so the real password never ends up in source control.
"""

import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )
