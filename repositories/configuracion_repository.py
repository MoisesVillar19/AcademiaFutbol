from database.connection import get_connection, fetch_one
from models.configuracion import Configuracion
from utils.dates import get_now


def obtener_configuracion() -> dict | None:
    return fetch_one("SELECT * FROM configuracion WHERE id_configuracion = 1")


def actualizar(config: Configuracion) -> None:
    conn = get_connection()
    now = get_now()
    conn.execute(
        """UPDATE configuracion SET
           nombre_academia = ?, direccion = ?, telefono = ?, correo = ?,
           mora_habilitada = ?, porcentaje_mora = ?, dias_por_vencer = ?,
           permitir_multiples_becas = ?, backup_automatico = ?,
           frecuencia_backup = ?, ruta_backup = ?, correo_onedrive = ?,
           fecha_actualizacion = ?
           WHERE id_configuracion = ?""",
        (
            config.nombre_academia,
            config.direccion,
            config.telefono,
            config.correo,
            config.mora_habilitada,
            config.porcentaje_mora,
            config.dias_por_vencer,
            config.permitir_multiples_becas,
            config.backup_automatico,
            config.frecuencia_backup,
            config.ruta_backup,
            config.correo_onedrive,
            now,
            config.id_configuracion,
        ),
    )
    conn.commit()
