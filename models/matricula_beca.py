from dataclasses import dataclass


@dataclass
class MatriculaBeca:
    id_matricula_beca: int | None = None
    id_matricula: int = 0
    id_beca: int = 0
    fecha_asignacion: str = ""
    activo: int = 1
    observacion: str = ""
