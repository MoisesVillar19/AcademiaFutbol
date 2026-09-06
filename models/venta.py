from dataclasses import dataclass


@dataclass
class Venta:
    id_venta: int | None = None
    id_estudiante: int | None = None
    id_usuario: int = 0
    fecha_venta: str = ""
    monto_total: float = 0.0
    metodo_pago: str = "EFECTIVO"
    tipo_venta: str = "UNIFORME"
    numero_recibo: str = ""
    comprobante_path: str | None = None
    activo: int = 1
