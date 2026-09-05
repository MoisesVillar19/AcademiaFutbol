from repositories import configuracion_repository
from models.configuracion import Configuracion
from services import auditoria_service
from utils.logger import logger


def obtener_configuracion() -> dict | None:
    return configuracion_repository.obtener_configuracion()


def actualizar_configuracion(data: dict) -> tuple[bool, str]:
    config = configuracion_repository.obtener_configuracion()
    if not config:
        return False, "Configuración no encontrada"

    config_obj = Configuracion(
        id_configuracion=config["id_configuracion"],
        nombre_academia=data.get("nombre_academia", config.get("nombre_academia", "")),
        direccion=data.get("direccion", config.get("direccion", "")),
        telefono=data.get("telefono", config.get("telefono", "")),
        correo=data.get("correo", config.get("correo", "")),
        mora_habilitada=data.get("mora_habilitada", config.get("mora_habilitada", 0)),
        tipo_mora=data.get("tipo_mora", config.get("tipo_mora", "PORCENTAJE")),
        porcentaje_mora=data.get("porcentaje_mora", config.get("porcentaje_mora", 0)),
        monto_mora=data.get("monto_mora", config.get("monto_mora", 0)),
        dias_por_vencer=data.get("dias_por_vencer", config.get("dias_por_vencer", 3)),
        permitir_multiples_becas=data.get("permitir_multiples_becas",
                                          config.get("permitir_multiples_becas", 1)),
        backup_automatico=data.get("backup_automatico", config.get("backup_automatico", 1)),
        frecuencia_backup=data.get("frecuencia_backup", config.get("frecuencia_backup", 7)),
        ruta_backup=data.get("ruta_backup", config.get("ruta_backup", "backups/")),
        correo_onedrive=data.get("correo_onedrive", config.get("correo_onedrive", "")),
    )

    configuracion_repository.actualizar(config_obj)

    auditoria_service.registrar_update(
        id_usuario=auditoria_service.id_usuario_sesion(),
        tabla="configuracion",
        id_registro=config["id_configuracion"],
        valores_anteriores=f"mora_habilitada={config.get('mora_habilitada', 0)}, porcentaje_mora={config.get('porcentaje_mora', 0)}, dias_por_vencer={config.get('dias_por_vencer', 3)}",
        valores_nuevos=f"mora_habilitada={config_obj.mora_habilitada}, porcentaje_mora={config_obj.porcentaje_mora}, dias_por_vencer={config_obj.dias_por_vencer}",
    )

    logger.info("Configuración actualizada")
    return True, "Configuración actualizada correctamente"


def obtener_dias_por_vencer() -> int:
    config = obtener_configuracion()
    return config.get("dias_por_vencer", 3) if config else 3


def esta_mora_habilitada() -> bool:
    config = obtener_configuracion()
    return bool(config.get("mora_habilitada", 0)) if config else False


def obtener_porcentaje_mora() -> float:
    config = obtener_configuracion()
    return config.get("porcentaje_mora", 0) if config else 0


def permite_multiples_becas() -> bool:
    config = obtener_configuracion()
    return bool(config.get("permitir_multiples_becas", 1)) if config else True


def obtener_valor(clave: str):
    """Retorna el valor crudo de una columna de CONFIGURACION (o None si no existe)."""
    config = obtener_configuracion()
    return config.get(clave) if config else None


def obtener_tipo_mora() -> str:
    config = obtener_configuracion()
    return (config.get("tipo_mora") or "PORCENTAJE") if config else "PORCENTAJE"


def obtener_monto_fijo_mora() -> float:
    config = obtener_configuracion()
    return float(config.get("monto_mora", 0) or 0) if config else 0.0
