import os
import psycopg2
import psycopg2.extras

DB = {
    "host": os.environ.get("POSTGRES_HOST", "localhost"),
    "dbname": os.environ.get("POSTGRES_DB", "library"),
    "user": os.environ.get("POSTGRES_USER", "user"),
    "password": os.environ.get("POSTGRES_PASSWORD", "password"),
    "port": os.environ.get("POSTGRES_PORT", 5432),
}

def db_conn():
    """
    Retorna uma conexão com o banco de dados PostgreSQL.
    """
    return psycopg2.connect(
        host=DB["host"],
        dbname=DB["dbname"],
        user=DB["user"],
        password=DB["password"],
        port=DB["port"],
        cursor_factory=psycopg2.extras.RealDictCursor,
    )