import sqlite3
from pathlib import Path

# Ruta absoluta hacia la base de datos
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "academia.db"


def get_connection():
    """
    Retorna una conexión SQLite configurada.
    """

    conn = sqlite3.connect(DB_PATH)

    # Permite acceder a columnas por nombre
    conn.row_factory = sqlite3.Row

    # Activa claves foráneas
    conn.execute("PRAGMA foreign_keys = ON")

    return conn