from dataclasses import dataclass


@dataclass
class StockAlmacen:
    id_stock: int | None = None
    id_producto: int = 0
    id_variante: int | None = None
    id_almacen: int = 0
    id_caja: int | None = None
    stock: int = 0
