from dataclasses import dataclass


@dataclass
class Egreso:
    id_egreso: int | None = None
    concepto: str = ""
    monto: float = 0.0
    fecha: str = ""
    responsable: str = ""
    id_usuario: int | None = None
    observacion: str = ""
    comprobante_path: str | None = None
    id_tarifa: int | None = None
    activo: int = 1
