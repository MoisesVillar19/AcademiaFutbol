from repositories import cuota_repository, pago_repository, estudiante_repository
from repositories import matricula_repository, beca_repository, producto_repository
from repositories import matricula_beca_repository
from utils.dates import get_today
from utils.excel_exporter import exportar_a_excel
import os


def reporte_morosos(ruta_archivo: str) -> tuple[bool, str]:
    cuotas = cuota_repository.obtener_vencidas()

    morosos = {}
    for c in cuotas:
        dni = c.get("dni", "")
        if dni not in morosos:
            morosos[dni] = {
                "dni": dni,
                "nombres": c.get("nombres", ""),
                "apellidos": c.get("apellidos", ""),
                "total_deuda": 0,
                "cuotas_vencidas": 0,
                "periodos": [],
            }
        morosos[dni]["total_deuda"] += c.get("saldo", 0)
        morosos[dni]["cuotas_vencidas"] += 1
        morosos[dni]["periodos"].append(c.get("periodo", ""))

    datos = []
    for m in morosos.values():
        datos.append({
            "dni": m["dni"],
            "estudiante": f"{m['nombres']} {m['apellidos']}",
            "cuotas_vencidas": m["cuotas_vencidas"],
            "total_deuda": round(m["total_deuda"], 2),
            "periodos": ", ".join(m["periodos"]),
        })

    columnas = [
        ("dni", "DNI"),
        ("estudiante", "Estudiante"),
        ("cuotas_vencidas", "Cuotas Vencidas"),
        ("total_deuda", "Total Deuda (S/)"),
        ("periodos", "Periodos"),
    ]

    return exportar_a_excel(datos, columnas, "Reporte de Morosos", ruta_archivo)


def reporte_pagos_por_fecha(fecha_inicio: str, fecha_fin: str,
                            ruta_archivo: str) -> tuple[bool, str]:
    pagos = pago_repository.obtener_por_fecha(fecha_inicio, fecha_fin)

    datos = []
    for p in pagos:
        datos.append({
            "numero_recibo": p.get("numero_recibo", ""),
            "fecha_pago": p.get("fecha_pago", ""),
            "monto_total": round(p.get("monto_total", 0), 2),
            "metodo_pago": p.get("metodo_pago", ""),
            "usuario": p.get("username", ""),
        })

    columnas = [
        ("numero_recibo", "N° Recibo"),
        ("fecha_pago", "Fecha de Pago"),
        ("monto_total", "Monto (S/)"),
        ("metodo_pago", "Método de Pago"),
        ("usuario", "Registrado por"),
    ]

    titulo = f"Pagos del {fecha_inicio} al {fecha_fin}"
    return exportar_a_excel(datos, columnas, titulo, ruta_archivo)


def reporte_ingresos_mensuales(ruta_archivo: str) -> tuple[bool, str]:
    today = get_today()
    fecha_inicio = today[:7] + "-01"

    from datetime import datetime, timedelta
    fecha = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    if fecha.month == 12:
        siguiente = fecha.replace(year=fecha.year + 1, month=1, day=1)
    else:
        siguiente = fecha.replace(month=fecha.month + 1, day=1)
    ultimo_dia = (siguiente - timedelta(days=1)).day
    fecha_fin = f"{today[:7]}-{ultimo_dia:02d}"

    pagos = pago_repository.obtener_por_fecha(fecha_inicio, fecha_fin)

    resumen_por_dia = {}
    for p in pagos:
        dia = p.get("fecha_pago", "")[:10]
        if dia not in resumen_por_dia:
            resumen_por_dia[dia] = {"fecha": dia, "cantidad": 0, "total": 0}
        resumen_por_dia[dia]["cantidad"] += 1
        resumen_por_dia[dia]["total"] += p.get("monto_total", 0)

    datos = []
    for dia_data in sorted(resumen_por_dia.values(), key=lambda x: x["fecha"]):
        datos.append({
            "fecha": dia_data["fecha"],
            "cantidad_pagos": dia_data["cantidad"],
            "total_ingresos": round(dia_data["total"], 2),
        })

    total_general = sum(d["total_ingresos"] for d in datos)
    total_pagos = sum(d["cantidad_pagos"] for d in datos)
    datos.append({
        "fecha": "TOTAL",
        "cantidad_pagos": total_pagos,
        "total_ingresos": round(total_general, 2),
    })

    columnas = [
        ("fecha", "Fecha"),
        ("cantidad_pagos", "Cantidad de Pagos"),
        ("total_ingresos", "Total Ingresos (S/)"),
    ]

    titulo = f"Ingresos Mensuales - {today[:7]}"
    return exportar_a_excel(datos, columnas, titulo, ruta_archivo)


def reporte_alumnos_por_categoria(ruta_archivo: str) -> tuple[bool, str]:
    matriculas = matricula_repository.obtener_activas()

    por_categoria = {}
    for m in matriculas:
        cat = m.get("categoria_nombre", "Sin categoría")
        if cat not in por_categoria:
            por_categoria[cat] = {"categoria": cat, "cantidad": 0, "estudiantes": []}
        por_categoria[cat]["cantidad"] += 1
        nombre = f"{m.get('nombres', '')} {m.get('apellidos', '')}"
        por_categoria[cat]["estudiantes"].append(nombre)

    datos = []
    for cat_data in por_categoria.values():
        datos.append({
            "categoria": cat_data["categoria"],
            "cantidad_alumnos": cat_data["cantidad"],
            "estudiantes": ", ".join(cat_data["estudiantes"][:5]) + (
                "..." if len(cat_data["estudiantes"]) > 5 else ""
            ),
        })

    total = sum(d["cantidad_alumnos"] for d in datos)
    datos.append({
        "categoria": "TOTAL",
        "cantidad_alumnos": total,
        "estudiantes": "",
    })

    columnas = [
        ("categoria", "Categoría"),
        ("cantidad_alumnos", "Cantidad de Alumnos"),
        ("estudiantes", "Estudiantes (muestra)"),
    ]

    return exportar_a_excel(datos, columnas, "Alumnos por Categoría", ruta_archivo)


def reporte_inventario(ruta_archivo: str) -> tuple[bool, str]:
    productos = producto_repository.obtener_todos(activo=1)

    datos = []
    for p in productos:
        estado = "OK"
        if p.get("stock_actual", 0) <= 0:
            estado = "SIN STOCK"
        elif p.get("stock_actual", 0) <= p.get("stock_minimo", 0):
            estado = "STOCK BAJO"

        datos.append({
            "codigo": p.get("codigo", ""),
            "nombre": p.get("nombre", ""),
            "categoria": p.get("categoria_nombre", ""),
            "tipo_uso": p.get("tipo_uso", ""),
            "stock_actual": p.get("stock_actual", 0),
            "stock_minimo": p.get("stock_minimo", 0),
            "precio": round(p.get("precio", 0), 2),
            "estado": estado,
        })

    columnas = [
        ("codigo", "Código"),
        ("nombre", "Nombre"),
        ("categoria", "Categoría"),
        ("tipo_uso", "Tipo de Uso"),
        ("stock_actual", "Stock Actual"),
        ("stock_minimo", "Stock Mínimo"),
        ("precio", "Precio (S/)"),
        ("estado", "Estado"),
    ]

    return exportar_a_excel(datos, columnas, "Reporte de Inventario", ruta_archivo)


def reporte_becas_activas(ruta_archivo: str) -> tuple[bool, str]:
    becas = beca_repository.obtener_todas(activo=1)

    datos = []
    for b in becas:
        datos.append({
            "nombre": b.get("nombre", ""),
            "tipo": b.get("tipo", ""),
            "valor": round(b.get("valor", 0), 2),
            "descripcion": b.get("descripcion", ""),
        })

    columnas = [
        ("nombre", "Nombre de Beca"),
        ("tipo", "Tipo"),
        ("valor", "Valor"),
        ("descripcion", "Descripción"),
    ]

    return exportar_a_excel(datos, columnas, "Becas Activas", ruta_archivo)


def listar_reportes() -> list[dict]:
    return [
        {"id": "morosos", "nombre": "Morosos", "descripcion": "Estudiantes con cuotas vencidas"},
        {"id": "pagos_fecha", "nombre": "Pagos por Fecha", "descripcion": "Historial de pagos en rango de fechas"},
        {"id": "ingresos_mensuales", "nombre": "Ingresos Mensuales", "descripcion": "Resumen de ingresos por mes"},
        {"id": "alumnos_categoria", "nombre": "Alumnos por Categoría", "descripcion": "Estudiantes activos por categoría"},
        {"id": "inventario", "nombre": "Inventario", "descripcion": "Estado actual del stock"},
        {"id": "becas_activas", "nombre": "Becas Activas", "descripcion": "Becas asignadas vigentes"},
    ]
