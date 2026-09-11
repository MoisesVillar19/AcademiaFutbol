"""Tests de backup y restore de base de datos."""
import os
import sqlite3


def _crear_db_temporal(ruta):
    conn = sqlite3.connect(ruta)
    conn.execute("CREATE TABLE demo (id INTEGER PRIMARY KEY, valor TEXT)")
    conn.execute("INSERT INTO demo (valor) VALUES ('original')")
    conn.commit()
    conn.close()


def test_create_backup_crea_archivo(tmp_path, monkeypatch):
    from database import backup
    ruta_bd = str(tmp_path / "fuente.db")
    _crear_db_temporal(ruta_bd)

    monkeypatch.setattr(backup, "DB_PATH", ruta_bd)
    destino = str(tmp_path / "backups")
    ruta_respaldo = backup.create_backup(custom_path=destino)

    assert os.path.exists(ruta_respaldo)
    assert os.path.basename(ruta_respaldo).startswith("academia_")
    assert os.path.getsize(ruta_respaldo) > 0


def test_resolver_fallback_local_si_central_caido(tmp_path, monkeypatch):
    from services import backup_service, configuracion_service
    import utils.constants as const
    # un ARCHIVO bloqueando la ruta simula share caído/sin permiso
    bloqueo = tmp_path / "bloqueo"
    bloqueo.write_text("x")
    monkeypatch.setattr(configuracion_service, "obtener_valor",
                        lambda k: str(bloqueo / "share"))
    monkeypatch.setattr(const, "BACKUP_DIR", str(tmp_path / "local"))
    assert backup_service._resolver_ruta_backup() == str(tmp_path / "local")


def test_crear_backup_usa_fallback_y_avisa(tmp_path, monkeypatch):
    from database import backup
    from services import backup_service, configuracion_service
    import utils.constants as const
    fuente = str(tmp_path / "fuente.db")
    _crear_db_temporal(fuente)
    monkeypatch.setattr(backup, "DB_PATH", fuente)
    bloqueo = tmp_path / "bloqueo"
    bloqueo.write_text("x")
    monkeypatch.setattr(configuracion_service, "obtener_valor",
                        lambda k: str(bloqueo / "share"))
    monkeypatch.setattr(const, "BACKUP_DIR", str(tmp_path / "local"))
    exito, msg, ruta = backup_service.crear_backup(id_usuario=1)
    assert exito is True
    assert os.path.exists(ruta)
    assert str(tmp_path / "local") in ruta
    assert "LOCAL" in msg


def test_restore_lock_segunda_pc_rechazada(tmp_path, monkeypatch):
    from services import backup_service, configuracion_service
    import utils.constants as const
    destino = str(tmp_path / "central")
    os.makedirs(destino, exist_ok=True)
    monkeypatch.setattr(configuracion_service, "obtener_valor", lambda k: destino)
    monkeypatch.setattr(const, "BACKUP_DIR", str(tmp_path / "local"))
    ok, _ = backup_service.adquirir_lock_restore()
    assert ok is True
    ocupado, info = backup_service.hay_restauracion_en_curso()
    assert ocupado is True and info
    ok2, msg2 = backup_service.adquirir_lock_restore()
    assert ok2 is False and "Otra PC" in msg2
    backup_service.liberar_lock_restore()
    ocupado, _ = backup_service.hay_restauracion_en_curso()
    assert ocupado is False


def test_restore_lock_rancio_se_toma(tmp_path, monkeypatch):
    import json
    import time
    from services import backup_service, configuracion_service
    import utils.constants as const
    destino = str(tmp_path / "central")
    os.makedirs(destino, exist_ok=True)
    monkeypatch.setattr(configuracion_service, "obtener_valor", lambda k: destino)
    monkeypatch.setattr(const, "BACKUP_DIR", str(tmp_path / "local"))
    with open(os.path.join(destino, ".restore_lock"), "w", encoding="utf-8") as f:
        json.dump({"pc": "MUERTA", "ts": time.time() - 3600 * 2}, f)
    ok, _ = backup_service.adquirir_lock_restore()
    assert ok is True
    backup_service.liberar_lock_restore()


def test_restaurar_con_lock_ajeno_no_toca_nada(tmp_path, monkeypatch, usuario_admin):
    from services import backup_service, configuracion_service
    import utils.constants as const
    destino = str(tmp_path / "central")
    os.makedirs(destino, exist_ok=True)
    pin_hash = configuracion_service.obtener_valor("pin_emergencia")
    assert pin_hash
    monkeypatch.setattr(configuracion_service, "obtener_valor",
                        lambda k: destino if k == "ruta_backup" else pin_hash)
    monkeypatch.setattr(const, "BACKUP_DIR", str(tmp_path / "local"))
    ok, _ = backup_service.adquirir_lock_restore()
    assert ok is True
    exito, msg = backup_service.restaurar_backup("inexistente.db", "roncalli2026")
    assert exito is False and "Otra PC" in msg
    # el lock sigue en pie (no lo liberó el intento fallido)
    ocupado, _ = backup_service.hay_restauracion_en_curso()
    assert ocupado is True
    backup_service.liberar_lock_restore()


def test_restaurar_libera_lock_al_terminar(tmp_path, monkeypatch, usuario_admin):
    from database import restore as restore_mod
    from services import backup_service, configuracion_service
    import utils.constants as const
    destino = str(tmp_path / "central")
    os.makedirs(destino, exist_ok=True)
    real = str(tmp_path / "real.db")
    _crear_db_temporal(real)
    monkeypatch.setattr(restore_mod, "DB_PATH", real)
    from services import configuracion_service as cs
    pin_hash = cs.obtener_valor("pin_emergencia")
    assert pin_hash
    monkeypatch.setattr(configuracion_service, "obtener_valor",
                        lambda k: destino if k == "ruta_backup" else pin_hash)
    monkeypatch.setattr(const, "BACKUP_DIR", str(tmp_path / "local"))
    # :memory: se evapora al cerrar conexión (artefacto solo de tests)
    from services import auditoria_service
    monkeypatch.setattr(auditoria_service, "registrar_log", lambda *a, **k: 1)
    respaldo = os.path.join(destino, "academia_2099-01-01_00-00-00.db")
    _crear_db_temporal(respaldo)
    exito, msg = backup_service.restaurar_backup(respaldo, "roncalli2026")
    assert exito is True, msg
    ocupado, _ = backup_service.hay_restauracion_en_curso()
    assert ocupado is False


def test_restore_recupera_datos_previos(tmp_path, monkeypatch):
    from database import backup, restore
    ruta_bd = str(tmp_path / "fuente.db")
    _crear_db_temporal(ruta_bd)

    monkeypatch.setattr(backup, "DB_PATH", ruta_bd)
    respaldo = backup.create_backup(custom_path=str(tmp_path))

    # Modificar la BD tras el backup
    conn = sqlite3.connect(ruta_bd)
    conn.execute("INSERT INTO demo (valor) VALUES ('posterior')")
    conn.commit()
    conn.close()

    monkeypatch.setattr(restore, "DB_PATH", ruta_bd)
    exito = restore.restore_backup(respaldo)
    assert exito is True

    # Verificar directamente sobre el archivo (la conexion global quedo cerrada)
    conn = sqlite3.connect(ruta_bd)
    filas = [r[0] for r in conn.execute("SELECT valor FROM demo").fetchall()]
    conn.close()
    assert filas == ["original"]


def test_restore_ruta_inexistente_lanza_error(tmp_path):
    from database import restore
    import pytest
    with pytest.raises(FileNotFoundError):
        restore.restore_backup(str(tmp_path / "no_existe.db"))
