import os
from collections.abc import Generator
from typing import Any

import psycopg
from psycopg.rows import dict_row


_open_connections: set[Any] = set()


def get_connection() -> Generator[psycopg.Connection[Any], None, None]:
    """Yield one server-side connection and close it after the request."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL must be configured")

    connection = psycopg.connect(database_url, row_factory=dict_row)
    _open_connections.add(connection)
    try:
        yield connection
    finally:
        _open_connections.discard(connection)
        connection.close()


def close_pool() -> None:
    """Close connections retained during application shutdown."""
    for connection in tuple(_open_connections):
        connection.close()
        _open_connections.discard(connection)
