import sqlite3
import os
import sys
import getpass

DB_NAME = os.getenv("DB_NAME", "academia.db")
DB_PATH = os.path.join(os.path.dirname(__file__), "database", DB_NAME)


def hash_password(password: str) -> str:
    from utils.security import hash_password as _hash
    return _hash(password)


def _verificar_pin(conn) -> bool:
    from utils.security import verify_password

    fila = conn.execute(
        "SELECT pin_emergencia FROM configuracion WHERE id_configuracion = 1"
    ).fetchone()
    if not fila or not fila["pin_emergencia"]:
        print("Error: El PIN de emergencia no está configurado en la base de datos.")
        return False

    pin = input("PIN de emergencia: ").strip()
    if not verify_password(pin, fila["pin_emergencia"]):
        print("Error: PIN incorrecto.")
        return False
    return True


def main():
    print("=" * 50)
    print("  RECUPERACIÓN DE CONTRASEÑA - Academia Deportiva")
    print("=" * 50)
    print()

    if not os.path.exists(DB_PATH):
        print(f"Error: No se encontró la base de datos en:")
        print(f"  {DB_PATH}")
        print()
        print("Asegúrese de ejecutar este script desde la carpeta del proyecto.")
        input("\nPresione Enter para salir...")
        sys.exit(1)

    print(f"Base de datos: {DB_PATH}")
    print()

    username = input("Usuario a restablecer: ").strip()
    if not username:
        print("Error: Debe ingresar un nombre de usuario.")
        input("\nPresione Enter para salir...")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    usuario = conn.execute(
        "SELECT * FROM usuario WHERE username = ?", (username,)
    ).fetchone()

    if not usuario:
        print(f"Error: No se encontró el usuario '{username}'.")
        conn.close()
        input("\nPresione Enter para salir...")
        sys.exit(1)

    print(f"Usuario encontrado: {username} (ID: {usuario['id_usuario']})")
    print()

    if not _verificar_pin(conn):
        conn.close()
        input("\nPresione Enter para salir...")
        sys.exit(1)

    print()
    print("PIN correcto. Ingrese la nueva contraseña.")
    print("La contraseña debe tener al menos 6 caracteres.")
    print()

    new_pass = getpass.getpass("Nueva contraseña: ")
    if len(new_pass) < 6:
        print("Error: La contraseña debe tener al menos 6 caracteres.")
        conn.close()
        input("\nPresione Enter para salir...")
        sys.exit(1)

    confirm = getpass.getpass("Confirme la contraseña: ")
    if new_pass != confirm:
        print("Error: Las contraseñas no coinciden.")
        conn.close()
        input("\nPresione Enter para salir...")
        sys.exit(1)

    print()
    confirmar = input("¿Restablecer contraseña? (s/n): ").strip().lower()
    if confirmar != "s":
        print("Operación cancelada.")
        conn.close()
        input("\nPresione Enter para salir...")
        sys.exit(0)

    password_hash = hash_password(new_pass)

    conn.execute(
        "UPDATE usuario SET password_hash = ? WHERE id_usuario = ?",
        (password_hash, usuario["id_usuario"]),
    )
    conn.commit()
    conn.close()

    print()
    print("Contraseña actualizada correctamente.")
    print()
    print("Puede iniciar sesión con:")
    print(f"  Usuario: {username}")
    print(f"  Contraseña: (la que acaba de definir)")
    print()

    input("Presione Enter para salir...")


if __name__ == "__main__":
    main()
