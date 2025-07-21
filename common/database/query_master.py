import os
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from typing import List, Dict, Any


def get_db_engine() -> Engine:
    """
    Create a SQLAlchemy engine using environment variables for connection options.
    Expected environment variables:
        DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, DB_DRIVER (optional, default: 'postgresql')
    """
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME")
    db_driver = os.getenv("DB_DRIVER", "postgresql")

    if not all([db_user, db_password, db_host, db_port, db_name]):
        raise ValueError("Database connection environment variables are not fully set.")

    db_url = f"{db_driver}://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(db_url)
    return engine


def query_to_json(query: str, params: dict[str, Any] | None = None) -> List[Dict[str, Any]]:
    """
    Execute a SQL query (as text) and return the results as a list of JSON (dicts).
    Args:
        query: SQL query string
        params: (Optional) Dictionary of parameters to bind to the SQL query.
            Keys are parameter names (as strings), values are the values to substitute.
            For example: {"user_id": 123}
    Returns:
        List of dictionaries representing rows
    """
    engine = get_db_engine()
    with engine.connect() as connection:
        result = connection.execute(text(query), params or {})
        rows = result.fetchall()
        columns = result.keys()
        return [dict(zip(columns, row)) for row in rows]
