import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


@pytest.fixture(autouse=True)
def test_db():
    """Base de datos en memoria para cada test."""
    import database.connection as conn_module
    import utils.constants as const_module

    # Guardar valores originales
    original_db_name = const_module.DB_NAME
    original_db_path = const_module.DB_PATH
    original_conn_db_path = getattr(conn_module, 'DB_PATH', None)

    # Cerrar conexión existente
    if conn_module._connection is not None:
        conn_module._connection.close()
        conn_module._connection = None

    # Forzar base de datos en memoria
    const_module.DB_NAME = ":memory:"
    const_module.DB_PATH = ":memory:"
    conn_module.DB_PATH = ":memory:"

    # Recrear tablas y seed
    from database.create_db import create_tables
    from database.seed import seed_database
    create_tables()
    seed_database()

    yield

    # Cleanup
    from database.connection import close_connection
    close_connection()
    const_module.DB_NAME = original_db_name
    const_module.DB_PATH = original_db_path
    if original_conn_db_path is not None:
        conn_module.DB_PATH = original_conn_db_path


@pytest.fixture
def usuario_admin():
    """Login como admin para tests que requieren sesión."""
    from services import auth_service
    auth_service.login("admin", "admin123")
    yield
    auth_service.logout()
