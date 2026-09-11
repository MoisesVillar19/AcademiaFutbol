"""R1 red LAN: journal adaptativo, timeout, cierre limpio."""
from database import connection as conn


def test_es_ruta_red_unc():
    assert conn.es_ruta_red("\\\\PC1\\Academia\\academia.db") is True
    assert conn.es_ruta_red("//PC1/Academia/academia.db") is True


def test_es_ruta_red_local():
    assert conn.es_ruta_red("C:\\datos\\academia.db") is False
    assert conn.es_ruta_red("database/academia.db") is False
    assert conn.es_ruta_red(":memory:") is False


def test_busy_timeout_configurado():
    c = conn.get_connection()
    row = c.execute("PRAGMA busy_timeout").fetchone()
    assert row[0] == conn.BUSY_TIMEOUT_MS


def test_cerrar_limpio_cierra_conexion():
    conn.get_connection()
    assert conn._connection is not None
    conn.cerrar_limpio()
    assert conn._connection is None
    # reabre sin error
    assert conn.get_connection() is not None


def test_transaccion_commit_y_rollback():
    with conn.transaccion():
        conn.execute_query("CREATE TABLE IF NOT EXISTS _t_red (id INTEGER PRIMARY KEY, v TEXT)")
        conn.execute_query("INSERT INTO _t_red (v) VALUES ('a')")
    assert conn.fetch_one("SELECT COUNT(*) as c FROM _t_red")["c"] >= 1
    try:
        with conn.transaccion():
            conn.execute_query("INSERT INTO _t_red (v) VALUES ('b')")
            raise ValueError("fuerza rollback")
    except ValueError:
        pass
    assert conn.fetch_all("SELECT v FROM _t_red WHERE v='b'") == []
    conn.execute_query("DROP TABLE IF EXISTS _t_red")
