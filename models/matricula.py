from dataclasses import dataclass


@dataclass
class Matricula:
    id_matricula: int | None = None
    id_estudiante: int = 0
    id_tarifa: int = 0
    monto_pactado: float | None = None
    fecha_inicio: str = ""
    fecha_fin: str = ""
    dia_vencimiento: int = 1
    estado: str = "ACTIVO"
    activo: int = 1
