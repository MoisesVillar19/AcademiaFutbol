import sqlite3

from repositories import venta_repository, detalle_venta_repository, producto_repository, movimiento_inventario_repository
from models.venta import Venta
from models.detalle_venta import DetalleVenta
from services import auditoria_service
from database.connection import transaccion
from utils.constants import METODO_EFECTIVO, METODO_YAPE, METODO_PLIN, METODO_TRANSFERENCIA
from utils.helpers import generate_receipt_number
from utils.dates import get_today
from utils.logger import logger

METODOS_VALIDOS = (METODO_EFECTIVO, METODO_YAPE, METODO_PLIN, METODO_TRANSFERENCIA)
TIPOS_VENTA_VALIDOS = ("UNIFORME", "TIENDA", "CAMPEONATO", "INSCRIPCION")


def registrar_venta(data: dict) -> tuple[bool, str, int | None]:
    """Venta flexible: uniformes (por tipo), tienda, campeonato. Descuenta stock atómicamente."""
    id_usuario = data.get("id_usuario") or auditoria_service.id_usuario_sesion()
    id_estudiante = data.get("id_estudiante")
    metodo = data.get("metodo_pago", METODO_EFECTIVO)
    tipo_venta = data.get("tipo_venta", "UNIFORME")
    items: list[dict] = data.get("items", [])  # [{id_producto, cantidad}]
    comprobante = data.get("comprobante_path")

    if not items:
        return False, "Debe incluir al menos un producto", None
    if metodo not in METODOS_VALIDOS:
        return False, "Método de pago no válido", None
    if tipo_venta not in TIPOS_VENTA_VALIDOS:
        return False, "Tipo de venta no válido", None
    if metodo != METODO_EFECTIVO and not comprobante and data.get("requiere_comprobante"):
        logger.warning(f"Venta {tipo_venta} sin comprobante para {metodo} (RN-042)")

    # Validación precio >0 flexible

    # Validar stock previo
    for it in items:
        prod = producto_repository.obtener_por_id(it["id_producto"])
        if not prod:
            return False, f"Producto {it['id_producto']} no encontrado", None
        if prod["stock_actual"] < it["cantidad"]:
            return False, f"Stock insuficiente de {prod['nombre']} (disp: {prod['stock_actual']})", None
        if prod["activo"] == 0:
            return False, f"Producto {prod['nombre']} desactivado", None

    total = sum(
        (producto_repository.obtener_por_id(it["id_producto"]) or {}).get("precio_venta", 0) * it["cantidad"]
        if not it.get("precio_unitario")
        else it["precio_unitario"] * it["cantidad"]
        for it in items
    )
    # Permitir monto pactado flexible (descuento)
    if data.get("monto_total") is not None:
        total = float(data["monto_total"])

    numero_recibo = data.get("numero_recibo") or generate_receipt_number()
    venta = Venta(
        id_estudiante=id_estudiante,
        id_usuario=id_usuario,
        fecha_venta=data.get("fecha_venta", get_today()),
        monto_total=round(total, 2),
        metodo_pago=metodo,
        tipo_venta=tipo_venta,
        numero_recibo=numero_recibo,
        comprobante_path=comprobante,
    )

    with transaccion():
        id_venta = None
        for _ in range(3):
            try:
                id_venta = venta_repository.insertar(venta)
                break
            except sqlite3.IntegrityError:
                venta.numero_recibo = generate_receipt_number()
        if id_venta is None:
            return False, "No se pudo generar recibo único", None

        for it in items:
            prod = producto_repository.obtener_por_id(it["id_producto"])
            stock_ant = prod["stock_actual"]
            stock_nuevo = stock_ant - it["cantidad"]
            precio_u = it.get("precio_unitario") or prod.get("precio_venta") or prod.get("precio") or 0
            detalle = DetalleVenta(
                id_venta=id_venta,
                id_producto=it["id_producto"],
                cantidad=it["cantidad"],
                precio_unitario=round(precio_u, 2),
                subtotal=round(precio_u * it["cantidad"], 2),
            )
            detalle_venta_repository.insertar(detalle)
            producto_repository.actualizar_stock(it["id_producto"], stock_nuevo)
            from models.movimiento_inventario import MovimientoInventario
            from utils.dates import get_now
            movimiento_inventario_repository.insertar(
                MovimientoInventario(
                    id_producto=it["id_producto"],
                    id_usuario=id_usuario,
                    tipo_movimiento="SALIDA",
                    cantidad=it["cantidad"],
                    stock_anterior=stock_ant,
                    stock_nuevo=stock_nuevo,
                    fecha_movimiento=get_now(),
                    motivo=f"Venta {tipo_venta} recibo {venta.numero_recibo}",
                )
            )

        auditoria_service.registrar_insert(id_usuario, "venta", id_venta, f"recibo={venta.numero_recibo}, total={total}, tipo={tipo_venta}")

    logger.info(f"Venta registrada: {venta.numero_recibo} total={total}")
    return True, f"Venta registrada. Recibo: {venta.numero_recibo}", id_venta


def registrar_inscripcion_con_uniforme(id_estudiante: int, id_usuario: int, id_producto_camiseta: int, metodo: str = METODO_EFECTIVO, comprobante: str | None = None) -> tuple[bool, str, int | None]:
    """RN-036: inscripción nuevo descuenta -1 camiseta (versión flexible)."""
    from services import configuracion_service
    precio = configuracion_service.obtener_valor("precio_inscripcion") or 100
    return registrar_venta(
        {
            "id_estudiante": id_estudiante,
            "id_usuario": id_usuario,
            "tipo_venta": "INSCRIPCION",
            "metodo_pago": metodo,
            "comprobante_path": comprobante,
            "monto_total": precio,
            "items": [{"id_producto": id_producto_camiseta, "cantidad": 1}],
        }
    )


def listar_ventas(fecha_inicio: str | None = None, fecha_fin: str | None = None, tipo_venta: str | None = None) -> list[dict]:
    return venta_repository.obtener_todos(fecha_inicio, fecha_fin, tipo_venta)


def obtener_venta(id_venta: int) -> dict | None:
    return venta_repository.obtener_por_id(id_venta)
