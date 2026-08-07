from services import importar_service
from utils.csv_parser import parse_csv, obtener_columnas_csv
from utils.excel_parser import parse_excel, obtener_hojas_excel, obtener_columnas_excel
from controllers import login_controller
from utils.logger import logger


def puede_acceder() -> bool:
    return login_controller.es_admin()


def cargar_archivo(ruta_archivo: str, hoja: str | None = None) -> tuple[bool, str, list[dict]]:
    extension = ruta_archivo.rsplit(".", 1)[-1].lower() if "." in ruta_archivo else ""

    if extension == "csv":
        return parse_csv(ruta_archivo)
    elif extension in ("xlsx", "xls"):
        return parse_excel(ruta_archivo, hoja)
    else:
        return False, "Formato no soportado. Use CSV o XLSX", []


def obtener_hojas(ruta_archivo: str) -> tuple[bool, str, list[str]]:
    extension = ruta_archivo.rsplit(".", 1)[-1].lower() if "." in ruta_archivo else ""

    if extension in ("xlsx", "xls"):
        return obtener_hojas_excel(ruta_archivo)

    return True, "OK", [""]


def obtener_columnas(ruta_archivo: str, hoja: str | None = None) -> tuple[bool, str, list[str]]:
    extension = ruta_archivo.rsplit(".", 1)[-1].lower() if "." in ruta_archivo else ""

    if extension == "csv":
        return obtener_columnas_csv(ruta_archivo)
    elif extension in ("xlsx", "xls"):
        return obtener_columnas_excel(ruta_archivo, hoja)

    return False, "Formato no soportado", []


def validar_datos(filas: list[dict], mapeo: dict | None = None) -> tuple[bool, str, list[str]]:
    if not filas:
        return False, "No hay datos para validar", []

    return importar_service.validar_filas(filas, mapeo)


def ejecutar_importacion(filas: list[dict], mapeo: dict | None = None) -> tuple[bool, str, dict]:
    if not filas:
        return False, "No hay datos para importar", {}

    usuario = login_controller.obtener_usuario_actual()
    id_usuario = usuario.get("id_usuario", 1) if usuario else 1

    return importar_service.importar_estudiantes(filas, id_usuario, mapeo)


def obtener_campos_sistema() -> list[str]:
    return importar_service.obtener_campos_disponibles()


def obtener_campos_obligatorios() -> list[str]:
    return importar_service.obtener_campos_obligatorios()


def obtener_campos_apoderado() -> list[str]:
    return importar_service.obtener_campos_apoderado()
