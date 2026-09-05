import sqlite3
import os
from contextlib import contextmanager
from utils.constants import DB_PATH


_nivel_transaccion: int = 0


class ConexionConTransaccion(sqlite3.Connection):
    """Conexion que pospone los commits individuales mientras haya una transaccion activa."""

    def commit(self):
        if _nivel_transaccion == 0:
            super().commit()


_connection: sqlite3.Connection | None = None


def get_connection() -> sqlite3.Connection:
    global _connection
    if _connection is None:
        dirname = os.path.dirname(DB_PATH)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        _connection = sqlite3.connect(DB_PATH, factory=ConexionConTransaccion)
        _connection.row_factory = sqlite3.Row
        _connection.execute("PRAGMA journal_mode=WAL")
        _connection.execute("PRAGMA foreign_keys=ON")
    return _connection


def close_connection() -> None:
    global _connection
    global _nivel_transaccion
    if _connection is not None:
        _connection.close()
        _connection = None
    _nivel_transaccion = 0


@contextmanager
def transaccion():
    """Agrupa escrituras en una sola transaccion atomica.

    Los commits de repositorios dentro del bloque se posponen hasta salir;
    si ocurre una excepcion se hace rollback de todo el bloque.
    """
    global _nivel_transaccion
    conn = get_connection()
    _nivel_transaccion += 1
    try:
        yield conn
        _nivel_transaccion -= 1
        if _nivel_transaccion == 0:
            conn.commit()
    except Exception:
        _nivel_transaccion -= 1
        if _nivel_transaccion <= 0:
            _nivel_transaccion = 0
            conn.rollback()
        raise


def execute_query(sql: str, params: tuple = ()) -> sqlite3.Cursor:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, params)
    conn.commit()
    return cursor


def fetch_one(sql: str, params: tuple = ()) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, params)
    row = cursor.fetchone()
    if row:
        return dict(row)
    return None


def fetch_all(sql: str, params: tuple = ()) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, params)
    return [dict(row) for row in cursor.fetchall()]
