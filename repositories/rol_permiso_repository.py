from database.connection import get_connection, fetch_all
from utils.constants import MODULOS_SISTEMA


def obtener_por_rol(rol: str) -> set:
    rows = fetch_all(
        "SELECT modulo FROM rol_permiso WHERE rol = ?",
        (rol,),
    )
    return {r["modulo"] for r in rows}


def reemplazar(rol: str, modulos) -> None:
    mods = [m.strip().lower() for m in (modulos or []) if m and str(m).strip()]
    invalidos = [m for m in mods if m not in MODULOS_SISTEMA]
    if invalidos:
        raise ValueError(f"Módulos no válidos: {', '.join(invalidos)}")
    conn = get_connection()
    conn.execute("DELETE FROM rol_permiso WHERE rol = ?", (rol,))
    for m in sorted(set(mods)):
        conn.execute(
            "INSERT INTO rol_permiso (rol, modulo) VALUES (?, ?)",
            (rol, m),
        )
    conn.commit()


def hay_datos() -> bool:
    rows = fetch_all("SELECT COUNT(*) AS c FROM rol_permiso")
    return bool(rows and rows[0]["c"])
