from services import reporte_service


def listar_reportes() -> list[dict]:
    return reporte_service.listar_reportes()


def reporte_morosos(ruta_archivo: str) -> tuple[bool, str]:
    return reporte_service.reporte_morosos(ruta_archivo)


def reporte_pagos_por_fecha(fecha_inicio: str, fecha_fin: str,
                            ruta_archivo: str) -> tuple[bool, str]:
    return reporte_service.reporte_pagos_por_fecha(fecha_inicio, fecha_fin, ruta_archivo)


def reporte_ingresos_mensuales(ruta_archivo: str) -> tuple[bool, str]:
    return reporte_service.reporte_ingresos_mensuales(ruta_archivo)


def reporte_alumnos_por_categoria(ruta_archivo: str) -> tuple[bool, str]:
    return reporte_service.reporte_alumnos_por_categoria(ruta_archivo)


def reporte_inventario(ruta_archivo: str) -> tuple[bool, str]:
    return reporte_service.reporte_inventario(ruta_archivo)


def reporte_becas_activas(ruta_archivo: str) -> tuple[bool, str]:
    return reporte_service.reporte_becas_activas(ruta_archivo)
