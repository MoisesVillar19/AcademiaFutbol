from dataclasses import dataclass


@dataclass
class Log:
    id_log: int | None = None
    id_usuario: int = 0
    tabla_afectada: str = ""
    id_registro: int = 0
    accion: str = ""
    valor_anterior: str = ""
    valor_nuevo: str = ""
    fecha: str = ""
