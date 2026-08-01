import os
import shutil
from database.connection import DB_PATH, close_connection


def restore_backup(backup_path: str) -> bool:
    if not os.path.exists(backup_path):
        raise FileNotFoundError(f"No se encontró el respaldo: {backup_path}")

    close_connection()
    shutil.copy2(backup_path, DB_PATH)
    return True


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python restore.py <ruta_del_respaldo>")
        sys.exit(1)

    restore_backup(sys.argv[1])
    print("Base de datos restaurada correctamente.")
