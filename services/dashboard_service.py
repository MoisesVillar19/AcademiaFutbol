from services import cuota_service, pago_service, inventario_service
from repositories import estudiante_repository, matricula_repository
from utils.dates import get_today
from datetime import datetime, timedelta


def obtener_indicadores() -> dict:
    alumnos_activos = estudiante_repository.obtener_todos(activo=1)
    total_activos = len(alumnos_activos)

    cuotas_vencidas = cuota_service.obtener_vencidas()
    total_vencidas = len(cuotas_vencidas)
    monto_vencido = sum(c.get("saldo", 0) for c in cuotas_vencidas)

    config = _obtener_configuracion()
    dias_por_vencer = config.get("dias_por_vencer", 3) if config else 3
    cuotas_por_vencer = cuota_service.obtener_por_vencer(dias_por_vencer)
    total_por_vencer = len(cuotas_por_vencer)
    monto_por_vencer = sum(c.get("saldo", 0) for c in cuotas_por_vencer)

    today = get_today()
    pagos_hoy = pago_service.contar_pagos_por_fecha(today, today)
    ingresos_hoy = pago_service.obtener_ingresos_por_fecha(today, today)

    fecha_inicio_mes = today[:7] + "-01"
    ultimo_dia = _ultimo_dia_mes(today)
    fecha_fin_mes = f"{today[:7]}-{ultimo_dia:02d}"
    ingresos_mes = pago_service.obtener_ingresos_por_fecha(fecha_inicio_mes, fecha_fin_mes)

    productos_bajo_stock = inventario_service.obtener_bajo_stock()
    total_bajo_stock = len(productos_bajo_stock)

    matriculas_mes = matricula_repository.contar_por_mes(fecha_inicio_mes, fecha_fin_mes)

    return {
        "alumnos_activos": total_activos,
        "cuotas_vencidas": total_vencidas,
        "monto_vencido": monto_vencido,
        "cuotas_por_vencer": total_por_vencer,
        "monto_por_vencer": monto_por_vencer,
        "pagos_hoy": pagos_hoy,
        "ingresos_hoy": ingresos_hoy,
        "ingresos_mes": ingresos_mes,
        "stock_bajo": total_bajo_stock,
        "productos_bajo_stock": productos_bajo_stock,
        "matriculas_mes": matriculas_mes,
    }


def listar_alumnos_activos() -> list[dict]:
    return estudiante_repository.obtener_todos(activo=1)


def listar_cuotas_vencidas() -> list[dict]:
    return cuota_service.obtener_vencidas()


def listar_cuotas_por_vencer() -> list[dict]:
    config = _obtener_configuracion()
    dias = config.get("dias_por_vencer", 3) if config else 3
    return cuota_service.obtener_por_vencer(dias)


def listar_pagos_hoy() -> list[dict]:
    today = get_today()
    return pago_service.listar_por_fecha(today, today)


def listar_monto_vencido() -> list[dict]:
    return cuota_service.obtener_vencidas()


def listar_monto_por_vencer() -> list[dict]:
    config = _obtener_configuracion()
    dias = config.get("dias_por_vencer", 3) if config else 3
    return cuota_service.obtener_por_vencer(dias)


def listar_stock_bajo() -> list[dict]:
    return inventario_service.obtener_bajo_stock()


def obtener_ingresos_por_dia_mes() -> list[dict]:
    today = get_today()
    fecha_inicio_mes = today[:7] + "-01"
    ultimo_dia = _ultimo_dia_mes(today)
    fecha_fin_mes = f"{today[:7]}-{ultimo_dia:02d}"

    pagos = pago_service.listar_por_fecha(fecha_inicio_mes, fecha_fin_mes)

    ingresos_por_dia = {}
    for pago in pagos:
        dia = pago.get("fecha_pago", "")[:10]
        if dia:
            if dia not in ingresos_por_dia:
                ingresos_por_dia[dia] = 0
            ingresos_por_dia[dia] += pago.get("monto_total", 0)

    resultado = []
    for dia in sorted(ingresos_por_dia.keys()):
        resultado.append({"dia": dia, "monto": ingresos_por_dia[dia]})

    return resultado


def contar_matriculas_mes() -> int:
    today = get_today()
    fecha_inicio_mes = today[:7] + "-01"
    ultimo_dia = _ultimo_dia_mes(today)
    fecha_fin_mes = f"{today[:7]}-{ultimo_dia:02d}"
    return matricula_repository.contar_por_mes(fecha_inicio_mes, fecha_fin_mes)


def _obtener_configuracion():
    from database.connection import fetch_one
    return fetch_one("SELECT * FROM configuracion WHERE id_configuracion = 1")


def _ultimo_dia_mes(fecha_str: str) -> int:
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
        if fecha.month == 12:
            siguiente = fecha.replace(year=fecha.year + 1, month=1, day=1)
        else:
            siguiente = fecha.replace(month=fecha.month + 1, day=1)
        ultimo = siguiente - timedelta(days=1)
        return ultimo.day
    except ValueError:
        return 30
