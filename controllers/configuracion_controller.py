from services import configuracion_service, categoria_service
from controllers import login_controller


def puede_acceder() -> bool:
    return login_controller.es_admin()


def obtener_configuracion() -> dict | None:
    return configuracion_service.obtener_configuracion()


def actualizar_configuracion(data: dict) -> tuple[bool, str]:
    if not puede_acceder():
        return False, "Acceso denegado: solo un administrador puede modificar la configuración"
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


def crear_backup_manual() -> tuple[bool, str, str | None]:
    if not puede_acceder():
        return False, "Acceso denegado: solo un administrador puede crear respaldos", None

    from services import backup_service
    return backup_service.crear_backup()


def verificar_backup_automatico() -> tuple[bool, str]:
    from services import backup_service
    return backup_service.verificar_backup_automatico()

def listar_backups() -> list[dict]:
    if not puede_acceder():
        return []
    from services import backup_service
    return backup_service.listar_backups()

def verificar_backup(ruta: str) -> tuple[bool, str]:
    if not puede_acceder():
        return False, "Solo ADMIN"
    from services import backup_service
    return backup_service.verificar_backup(ruta)

def restaurar_backup(ruta: str, pin: str) -> tuple[bool, str]:
    if not puede_acceder():
        return False, "Solo ADMIN"
    from services import backup_service
    return backup_service.restaurar_backup(ruta, pin)

def rotar_backups(dias: int = 30) -> int:
    if not puede_acceder():
        return 0
    from services import backup_service
    return backup_service.rotar_backups(dias)
