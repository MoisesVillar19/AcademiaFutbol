from dataclasses import dataclass, field


@dataclass
class Persona:
    id_persona: int | None = None
    dni: str = ""
    tipo_documento: str = "DNI"
    nombres: str = ""
    apellidos: str = ""
    fecha_nacimiento: str = ""
    sexo: str = ""
    direccion: str = ""
    telefono: str = ""
    correo: str = ""
    activo: int = 1
    fecha_creacion: str = ""
    fecha_actualizacion: str = ""
