import os

import psycopg


def get_database_connection():
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres@localhost:5432/urban_aanchol",
    )

    return psycopg.connect(database_url)