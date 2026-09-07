from dataclasses import dataclass


@dataclass
class Estudiante:
    id_estudiante: int | None = None
    id_persona: int = 0
    estado: str = "ACTIVO"
    fecha_ingreso: str = ""
    fecha_retiro: str | None = None
    es_nuevo: int = 0
    foto_path: str | None = None
    comprobante_pago_path: str | None = None
    fecha_matricula: str | None = None
    activo: int = 1
