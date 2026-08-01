from dataclasses import dataclass


@dataclass
class Usuario:
    id_usuario: int | None = None
    id_persona: int = 0
    username: str = ""
    password_hash: str = ""
    rol: str = ""
    activo: int = 1
    fecha_creacion: str = ""
    fecha_actualizacion: str = ""
