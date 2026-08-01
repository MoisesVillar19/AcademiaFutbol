import os
import shutil
from datetime import datetime
from database.connection import DB_PATH
from utils.constants import BACKUP_DIR


def create_backup(custom_path: str | None = None) -> str:
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError("No se encontró la base de datos.")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"academia_{timestamp}.db"

    if custom_path:
        dest_dir = custom_path
    else:
        dest_dir = BACKUP_DIR

    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, filename)
    shutil.copy2(DB_PATH, dest_path)
    return dest_path


if __name__ == "__main__":
    path = create_backup()
    print(f"Backup creado: {path}")
