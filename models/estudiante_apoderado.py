from dataclasses import dataclass


@dataclass
class EstudianteApoderado:
    id_estudiante_apoderado: int | None = None
    id_estudiante: int = 0
    id_apoderado: int = 0
    es_principal: int = 0
    activo: int = 1
