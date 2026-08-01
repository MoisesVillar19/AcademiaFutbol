from dataclasses import dataclass


@dataclass
class Configuracion:
    id_configuracion: int | None = None
    nombre_academia: str = ""
    direccion: str = ""
    telefono: str = ""
    correo: str = ""
    mora_habilitada: int = 0
    porcentaje_mora: float = 0.0
    dias_por_vencer: int = 3
    permitir_multiples_becas: int = 1
    backup_automatico: int = 1
    frecuencia_backup: int = 7
    ruta_backup: str = "backups/"
    correo_onedrive: str = ""
    fecha_actualizacion: str = ""
