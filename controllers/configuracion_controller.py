from services import configuracion_service, categoria_service
from controllers import login_controller


def puede_acceder() -> bool:
    return login_controller.es_admin()


def obtener_configuracion() -> dict | None:
    return configuracion_service.obtener_configuracion()


def actualizar_configuracion(data: dict) -> tuple[bool, str]:
    return configuracion_service.actualizar_configuracion(data)


def obtener_dias_por_vencer() -> int:
    return configuracion_service.obtener_dias_por_vencer()


def esta_mora_habilitada() -> bool:
    return configuracion_service.esta_mora_habilitada()


def obtener_porcentaje_mora() -> float:
    return configuracion_service.obtener_porcentaje_mora()


def permite_multiples_becas() -> bool:
    return configuracion_service.permite_multiples_becas()


def listar_categorias() -> list[dict]:
    return categoria_service.listar_categorias()
