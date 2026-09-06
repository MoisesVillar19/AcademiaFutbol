import json
import os
import sys
import shutil
import zipfile
import tempfile
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

from updater.config import (
    GITHUB_API_URL,
    GITHUB_DOWNLOAD_URL,
    FRECUENCIA_VERIFICACION_HORAS,
    APP_EXE_NAME,
    RECORDAR_RECHAZO,
)
from utils.constants import __version__

# Archivo para guardar estado del updater
_STATE_DIR = os.path.join(os.path.expanduser("~"), ".academia_futbol")
_STATE_FILE = os.path.join(_STATE_DIR, "updater_state.json")


def _cargar_estado() -> dict:
    try:
        with open(_STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _guardar_estado(estado: dict) -> None:
    os.makedirs(_STATE_DIR, exist_ok=True)
    with open(_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(estado, f, indent=2)


def _obtener_ruta_app() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(__file__))


def comparar_versiones(v_local: str, v_remota: str) -> int:
    partes_local = [int(x) for x in v_local.split(".")]
    partes_remota = [int(x) for x in v_remota.split(".")]
    for l, r in zip(partes_local, partes_remota):
        if l < r:
            return -1
        if l > r:
            return 1
    if len(partes_local) < len(partes_remota):
        return -1
    if len(partes_local) > len(partes_remota):
        return 1
    return 0


def debe_verificar() -> bool:
    estado = _cargar_estado()
    if not RECORDAR_RECHAZO and estado.get("rechazado_version"):
        return True
    ultima_verificacion = estado.get("ultima_verificacion")
    if not ultima_verificacion:
        return True
    try:
        fecha = datetime.fromisoformat(ultima_verificacion)
        return datetime.now() - fecha > timedelta(hours=FRECUENCIA_VERIFICACION_HORAS)
    except (ValueError, TypeError):
        return True


def verificar_actualizacion() -> dict | None:
    try:
        req = urllib.request.Request(
            GITHUB_API_URL,
            headers={"Accept": "application/vnd.github.v3+json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        tag = data.get("tag_name", "").lstrip("v")
        if not tag:
            return None

        if comparar_versiones(__version__, tag) >= 0:
            _guardar_estado({
                "ultima_verificacion": datetime.now().isoformat(),
                "ultima_version_verificada": tag,
            })
            return None

        assets = data.get("assets", [])
        zip_url = None
        for asset in assets:
            nombre = asset.get("name", "")
            if nombre.endswith(".zip") and "AcademiaFutbol" in nombre:
                zip_url = asset.get("browser_download_url")
                break

        if not zip_url:
            zip_url = f"{GITHUB_DOWNLOAD_URL}/v{tag}/AcademiaFutbol-v{tag}.zip"

        return {
            "version": tag,
            "nombre": data.get("name", f"v{tag}"),
            "descripcion": data.get("body", "Sin descripción"),
            "url_descarga": zip_url,
            "fecha": data.get("published_at", ""),
        }

    except Exception:
        return None


def registrar_verificacion() -> None:
    estado = _cargar_estado()
    estado["ultima_verificacion"] = datetime.now().isoformat()
    _guardar_estado(estado)


def registrar_rechazo(version: str) -> None:
    estado = _cargar_estado()
    estado["rechazado_version"] = version
    estado["ultima_verificacion"] = datetime.now().isoformat()
    _guardar_estado(estado)


def descargar_y_actualizar(url_descarga: str, callback_progreso=None) -> bool:
    try:
        req = urllib.request.Request(url_descarga)
        with urllib.request.urlopen(req, timeout=60) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            datos = b""
            bytesRead = 0
            while True:
                chunk = resp.read(8192)
                if not chunk:
                    break
                datos += chunk
                bytesRead += len(chunk)
                if callback_progreso and total > 0:
                    callback_progreso(bytesRead, total)

        ruta_temp = tempfile.mkdtemp()
        ruta_zip = os.path.join(ruta_temp, "update.zip")
        with open(ruta_zip, "wb") as f:
            f.write(datos)

        ruta_app = _obtener_ruta_app()

        with zipfile.ZipFile(ruta_zip, "r") as zf:
            nombres = zf.namelist()
            for nombre in nombres:
                if nombre.endswith("/"):
                    continue
                # NO sobrescribir datos del usuario ni config local
                lower = nombre.lower()
                if lower in ("config.ini", "config_visual.json"):
                    continue
                if lower.startswith("database/academia.db") or lower.startswith("database\\academia.db"):
                    continue
                if lower.startswith("database/") and lower.endswith(".db"):
                    continue
                if lower.startswith("logs/") or lower.startswith("logs\\"):
                    continue
                if lower.startswith("backups/") or lower.startswith("backups\\"):
                    continue
                # Actualizar código de la BD sí (create_db.py etc.)
                destino = os.path.join(ruta_app, nombre)
                os.makedirs(os.path.dirname(destino), exist_ok=True)
                with zf.open(nombre) as src, open(destino, "wb") as dst:
                    dst.write(src.read())

        shutil.rmtree(ruta_temp, ignore_errors=True)

        _guardar_estado({
            "ultima_verificacion": datetime.now().isoformat(),
            "actualizado_version": __version__,
        })

        return True

    except Exception:
        return False


def reiniciar_app() -> None:
    ruta_app = _obtener_ruta_app()
    exe_path = os.path.join(ruta_app, APP_EXE_NAME)
    if os.path.exists(exe_path):
        os.startfile(exe_path)
    sys.exit(0)
