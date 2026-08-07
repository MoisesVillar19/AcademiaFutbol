from repositories import usuario_repository, persona_repository
from models.usuario import Usuario
from models.persona import Persona
from services import auditoria_service
from utils.security import hash_password, generate_temp_password
from utils.logger import logger


def crear_usuario(persona_data: dict, username: str, rol: str) -> tuple[bool, str, int | None]:
    if usuario_repository.existe_username(username):
        return False, "El nombre de usuario ya existe", None

    dni = persona_data.get("dni", "")
    if usuario_repository.persona_tiene_usuario(persona_data.get("id_persona", 0)):
        return False, "Esta persona ya tiene un usuario asociado", None

    persona = Persona(
        id_persona=persona_data.get("id_persona"),
        dni=dni,
        nombres=persona_data.get("nombres", ""),
        apellidos=persona_data.get("apellidos", ""),
        fecha_nacimiento=persona_data.get("fecha_nacimiento", ""),
        sexo=persona_data.get("sexo", ""),
        direccion=persona_data.get("direccion", ""),
        telefono=persona_data.get("telefono", ""),
        correo=persona_data.get("correo", ""),
    )

    if persona.id_persona:
        persona_repository.actualizar(persona)
        id_persona = persona.id_persona
    else:
        if persona_repository.existe_dni(dni):
            return False, "El DNI ya está registrado", None
        id_persona = persona_repository.insertar(persona)

    temp_password = generate_temp_password()
    usuario = Usuario(
        id_persona=id_persona,
        username=username,
        password_hash=hash_password(temp_password),
        rol=rol,
    )

    id_usuario = usuario_repository.insertar(usuario)

    auditoria_service.registrar_insert(
        id_usuario=1,
        tabla="usuario",
        id_registro=id_usuario,
        valores_nuevos=f"username={username}, rol={rol}, id_persona={id_persona}",
    )

    logger.info(f"Usuario creado: '{username}' (rol: {rol})")
    return True, temp_password, id_usuario


def editar_usuario(id_usuario: int, data: dict) -> tuple[bool, str]:
    usuario = usuario_repository.obtener_por_id(id_usuario)
    if not usuario:
        return False, "Usuario no encontrado"

    username = data.get("username", usuario["username"])
    rol = data.get("rol", usuario["rol"])

    if usuario_repository.existe_username(username, exclude_id=id_usuario):
        return False, "El nombre de usuario ya existe"

    persona = Persona(
        id_persona=usuario["id_persona"],
        dni=data.get("dni", ""),
        nombres=data.get("nombres", ""),
        apellidos=data.get("apellidos", ""),
        fecha_nacimiento=data.get("fecha_nacimiento", ""),
        sexo=data.get("sexo", ""),
        direccion=data.get("direccion", ""),
        telefono=data.get("telefono", ""),
        correo=data.get("correo", ""),
    )
    persona_repository.actualizar(persona)

    password_hash = usuario["password_hash"]
    if data.get("password"):
        password_hash = hash_password(data["password"])

    usuario_obj = Usuario(
        id_usuario=id_usuario,
        id_persona=usuario["id_persona"],
        username=username,
        password_hash=password_hash,
        rol=rol,
        activo=usuario["activo"],
    )
    usuario_repository.actualizar(usuario_obj)

    auditoria_service.registrar_update(
        id_usuario=1,
        tabla="usuario",
        id_registro=id_usuario,
        valores_anteriores=f"username={usuario['username']}, rol={usuario['rol']}",
        valores_nuevos=f"username={username}, rol={rol}",
    )

    logger.info(f"Usuario editado: ID={id_usuario}")
    return True, "Usuario actualizado correctamente"


def activar_usuario(id_usuario: int) -> tuple[bool, str]:
    usuario = usuario_repository.obtener_por_id(id_usuario)
    if not usuario:
        return False, "Usuario no encontrado"

    if usuario["activo"] == 1:
        return False, "El usuario ya está activo"

    usuario_obj = Usuario(
        id_usuario=id_usuario,
        id_persona=usuario["id_persona"],
        username=usuario["username"],
        password_hash=usuario["password_hash"],
        rol=usuario["rol"],
        activo=1,
    )
    usuario_repository.actualizar(usuario_obj)

    auditoria_service.registrar_log(
        id_usuario=1,
        tabla_afectada="usuario",
        id_registro=id_usuario,
        accion="ACTIVACION",
        valor_anterior="activo=0",
        valor_nuevo="activo=1",
    )

    logger.info(f"Usuario activado: ID={id_usuario}")
    return True, "Usuario activado correctamente"


def desactivar_usuario(id_usuario: int) -> tuple[bool, str]:
    usuario = usuario_repository.obtener_por_id(id_usuario)
    if not usuario:
        return False, "Usuario no encontrado"

    if usuario["activo"] == 0:
        return False, "El usuario ya está desactivado"

    from utils.constants import DEFAULT_ADMIN_USER
    if usuario["username"] == DEFAULT_ADMIN_USER:
        return False, "No se puede desactivar el usuario administrador principal"

    usuario_repository.soft_delete(id_usuario)

    auditoria_service.registrar_desactivacion(
        id_usuario=1,
        tabla="usuario",
        id_registro=id_usuario,
        valores_anteriores="activo=1",
        valor_nuevos="activo=0",
    )

    logger.info(f"Usuario desactivado: ID={id_usuario}")
    return True, "Usuario desactivado correctamente"


def restablecer_password(id_usuario: int) -> tuple[bool, str, str]:
    usuario = usuario_repository.obtener_por_id(id_usuario)
    if not usuario:
        return False, "Usuario no encontrado", ""

    temp_password = generate_temp_password()
    usuario_repository.cambiar_password(id_usuario, hash_password(temp_password))

    auditoria_service.registrar_log(
        id_usuario=1,
        tabla_afectada="usuario",
        id_registro=id_usuario,
        accion="RESTABLECER_PASSWORD",
    )

    logger.info(f"Password restablecido: ID={id_usuario}")
    return True, "Contraseña restablecida correctamente", temp_password


def listar_usuarios(activo: int | None = None) -> list[dict]:
    return usuario_repository.obtener_todos(activo=activo)


def obtener_usuario(id_usuario: int) -> dict | None:
    return usuario_repository.obtener_por_id(id_usuario)
