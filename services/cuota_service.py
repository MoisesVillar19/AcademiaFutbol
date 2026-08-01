from repositories import cuota_repository
from models.cuota import Cuota
from utils.dates import get_today
from datetime import datetime, timedelta


def crear_cuota(id_matricula: int, monto_total: float, fecha_vencimiento: str,
               periodo: str) -> int:
    cuota = Cuota(
        id_matricula=id_matricula,
        periodo=periodo,
        fecha_vencimiento=fecha_vencimiento,
        monto_total=monto_total,
        monto_pagado=0,
        saldo=monto_total,
        estado="PENDIENTE",
    )
    return cuota_repository.insertar(cuota)


def generar_siguiente_cuota(id_matricula: int, monto_base: float,
                            dia_vencimiento: int) -> tuple[bool, str, int | None]:
    cuotas = cuota_repository.obtener_por_matricula(id_matricula)

    if cuotas:
        ultimo_periodo = cuotas[-1]["periodo"]
        try:
            fecha = datetime.strptime(ultimo_periodo, "%Y-%m")
            nueva_fecha = fecha + timedelta(days=32)
            siguiente_periodo = nueva_fecha.strftime("%Y-%m")
        except ValueError:
            siguiente_periodo = get_today()[:7]
    else:
        siguiente_periodo = get_today()[:7]

    fecha_venc = f"{siguiente_periodo}-{str(dia_vencimiento).zfill(2)}"

    id_cuota = crear_cuota(
        id_matricula=id_matricula,
        monto_total=monto_base,
        fecha_vencimiento=fecha_venc,
        periodo=siguiente_periodo,
    )

    return True, "Cuota generada correctamente", id_cuota


def actualizar_pago(id_cuota: int, monto_pagado: float) -> tuple[bool, str]:
    cuota = cuota_repository.obtener_por_id(id_cuota)
    if not cuota:
        return False, "Cuota no encontrada"

    nuevo_monto_pagado = cuota["monto_pagado"] + monto_pagado
    nuevo_saldo = cuota["monto_total"] - nuevo_monto_pagado

    if nuevo_saldo < 0:
        return False, "El monto excede el saldo pendiente"

    if nuevo_saldo == 0:
        estado = "PAGADO"
    elif nuevo_monto_pagado > 0:
        estado = "PARCIAL"
    else:
        estado = "PENDIENTE"

    cuota_obj = Cuota(
        id_cuota=id_cuota,
        id_matricula=cuota["id_matricula"],
        periodo=cuota["periodo"],
        fecha_vencimiento=cuota["fecha_vencimiento"],
        monto_total=cuota["monto_total"],
        monto_pagado=nuevo_monto_pagado,
        saldo=nuevo_saldo,
        estado=estado,
        activo=cuota["activo"],
    )
    cuota_repository.actualizar(cuota_obj)

    return True, f"Pago registrado. Saldo: S/{nuevo_saldo:.2f}"


def actualizar_estados_vencidos() -> int:
    today = get_today()
    cuotas = cuota_repository.obtener_todas_pendientes()

    actualizadas = 0
    for cuota in cuotas:
        if cuota["fecha_vencimiento"] < today and cuota["saldo"] > 0:
            cuota_obj = Cuota(
                id_cuota=cuota["id_cuota"],
                id_matricula=cuota["id_matricula"],
                periodo=cuota["periodo"],
                fecha_vencimiento=cuota["fecha_vencimiento"],
                monto_total=cuota["monto_total"],
                monto_pagado=cuota["monto_pagado"],
                saldo=cuota["saldo"],
                estado="VENCIDO",
                activo=cuota["activo"],
            )
            cuota_repository.actualizar(cuota_obj)
            actualizadas += 1

    return actualizadas


def obtener_cuotas_por_matricula(id_matricula: int) -> list[dict]:
    return cuota_repository.obtener_por_matricula(id_matricula)


def obtener_cuotas_pendientes(id_matricula: int) -> list[dict]:
    return cuota_repository.obtener_pendientes_por_matricula(id_matricula)


def contar_por_estado(estado: str) -> int:
    return cuota_repository.contar_por_estado(estado)


def obtener_vencidas() -> list[dict]:
    return cuota_repository.obtener_vencidas()


def obtener_por_vencer(dias: int = 3) -> list[dict]:
    return cuota_repository.obtener_por_vencer(dias)
