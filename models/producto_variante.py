from dataclasses import dataclass


@dataclass
class ProductoVariante:
    id_variante: int | None = None
    id_producto: int = 0
    id_talla: int | None = None
    sku: str = ""
    codigo_barras: str = ""
    stock_minimo: int = 0
    activo: int = 1
