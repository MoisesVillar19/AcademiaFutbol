from dataclasses import dataclass


@dataclass
class DetalleVenta:
    id_detalle_venta: int | None = None
    id_venta: int = 0
    id_producto: int = 0
    cantidad: int = 0
    precio_unitario: float = 0.0
    subtotal: float = 0.0
    id_variante: int | None = None
    id_lote: int | None = None
