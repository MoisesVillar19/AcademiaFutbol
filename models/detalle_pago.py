from dataclasses import dataclass


@dataclass
class DetallePago:
    id_detalle_pago: int | None = None
    id_pago: int = 0
    id_cuota: int = 0
    monto_pagado: float = 0.0
