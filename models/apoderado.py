from dataclasses import dataclass


@dataclass
class Apoderado:
    id_apoderado: int | None = None
    id_persona: int = 0
    parentesco: str = ""
    ocupacion: str = ""
    activo: int = 1
    fecha_creacion: str = ""
    fecha_actualizacion: str = ""
