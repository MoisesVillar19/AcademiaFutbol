from dataclasses import dataclass


@dataclass
class Lote:
    id_lote: int | None = None
    id_producto: int = 0
    id_variante: int | None = None
    id_almacen: int = 0
    codigo_lote: str = ""
    fecha_ingreso: str = ""
    fecha_caducidad: str = ""
    id_proveedor: int | None = None
    cantidad: int = 0
    stock_restante: int = 0
