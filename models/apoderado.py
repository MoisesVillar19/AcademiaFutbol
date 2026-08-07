from dataclasses import dataclass


@dataclass
class Apoderado:
    id_apoderado: int | None = None
    id_persona: int = 0
    tipo_documento: str = "DNI"
    parentesco: str = ""
    ocupacion: str = ""
    telefono: str = ""
    direccion: str = ""
    activo: int = 1
    fecha_creacion: str = ""
    fecha_actualizacion: str = ""
