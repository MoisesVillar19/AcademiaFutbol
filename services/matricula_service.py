from repositories import matricula_repository, matricula_beca_repository, estudiante_repository
from models.matricula import Matricula
from services import auditoria_service, cuota_service, beca_service
from database.connection import transaccion
from utils.constants import STATUS_ACTIVO, STATUS_REINGRESANTE
from utils.dates import get_today
from utils.logger import logger


def crear_matricula(data: dict, id_usuario: int = 1) -> tuple[bool, str, int | None]:
    id_estudiante = data.get("id_estudiante")
    id_tarifa = data.get("id_tarifa")

    if not id_estudiante:
        return False, "El estudiante es obligatorio", None
    if not id_tarifa:
        return False, "La tarifa es obligatoria", None

    estudiante = estudiante_repository.obtener_por_id(id_estudiante)
    if not estudiante:
        return False, "Estudiante no encontrado", None

    matriculas_existentes = matricula_repository.obtener_por_estudiante(id_estudiante)
    for m in matriculas_existentes:
        if m["estado"] == "ACTIVO":
            return False, "El estudiante ya tiene una matrícula activa", None

    monto_pactado = data.get("monto_pactado")
    dia_vencimiento = data.get("dia_vencimiento", 1)

    becas_asignadas = data.get("becas", [])
    if len(becas_asignadas) > 1:
        from services import configuracion_service
        if not configuracion_service.permite_multiples_becas():
            return False, "La configuración actual no permite múltiples becas por matrícula", None

    matricula = Matricula(
        id_estudiante=id_estudiante,
        id_tarifa=id_tarifa,
        monto_pactado=monto_pactado,
        fecha_inicio=data.get("fecha_inicio", get_today()),
        dia_vencimiento=dia_vencimiento,
        estado=STATUS_ACTIVO,
    )

    from repositories import tarifa_repository
    tarifa_data = tarifa_repository.obtener_por_id(id_tarifa)
    monto_base = monto_pactado if monto_pactado is not None else tarifa_data["monto"]

    with transaccion():
        id_matricula = matricula_repository.insertar(matricula)

        for beca_info in becas_asignadas:
            id_beca = beca_info.get("id_beca")
            beca_data = beca_service.obtener_beca(id_beca)
            if beca_data:
                if beca_data["tipo"] == "PORCENTAJE":
                    descuento = monto_base * (beca_data["valor"] / 100)
                    monto_base -= descuento
                else:
                    monto_base -= beca_data["valor"]

                matricula_beca_repository.insertar(
                    id_matricula=id_matricula,
                    id_beca=id_beca,
                    observacion=beca_info.get("observacion", ""),
                )

        monto_base = round(max(monto_base, 0), 2)

        cuota_service.generar_siguiente_cuota(
            id_matricula=id_matricula,
            monto_base=monto_base,
            dia_vencimiento=dia_vencimiento,
        )

        if estudiante["estado"] == STATUS_REINGRESANTE:
            estudiante_repository.cambiar_estado(id_estudiante, STATUS_ACTIVO)

        auditoria_service.registrar_insert(
            id_usuario=id_usuario,
            tabla="matricula",
            id_registro=id_matricula,
            valores_nuevos=f"id_estudiante={id_estudiante}, id_tarifa={id_tarifa}, monto={monto_base}",
        )

    logger.info(f"Matrícula creada: ID={id_matricula}, estudiante={id_estudiante}")
    return True, "Matrícula registrada correctamente", id_matricula


def obtener_matricula(id_matricula: int) -> dict | None:
    return matricula_repository.obtener_por_id(id_matricula)


def obtener_por_estudiante(id_estudiante: int) -> list[dict]:
    return matricula_repository.obtener_por_estudiante(id_estudiante)


def listar_matriculas_activas() -> list[dict]:
    return matricula_repository.obtener_activas()


def asignar_beca(id_matricula: int, id_beca: int,
                 observacion: str = "") -> tuple[bool, str]:
    beca = beca_service.obtener_beca(id_beca)
    if not beca:
        return False, "Beca no encontrada"

    actuales = [
        b for b in matricula_beca_repository.obtener_por_matricula(id_matricula)
        if b.get("activo", 1)
    ]
    if actuales:
        from services import configuracion_service
        if not configuracion_service.permite_multiples_becas():
            return False, "La configuración actual no permite múltiples becas por matrícula"

    matricula_beca_repository.insertar(id_matricula, id_beca, observacion)

    auditoria_service.registrar_insert(
        id_usuario=auditoria_service.id_usuario_sesion(),
        tabla="matricula_beca",
        id_registro=id_matricula,
        valores_nuevos=f"id_beca={id_beca}, observacion={observacion}",
    )

    return True, "Beca asignada correctamente"


def desasignar_beca(id_matricula: int, id_beca: int) -> tuple[bool, str]:
    matricula_beca_repository.eliminar(id_matricula, id_beca)

    auditoria_service.registrar_desactivacion(
        id_usuario=auditoria_service.id_usuario_sesion(),
        tabla="matricula_beca",
        id_registro=id_matricula,
        valores_anteriores=f"id_beca={id_beca}, activo=1",
        valores_nuevos="activo=0",
    )

    return True, "Beca desasignada correctamente"


def obtener_becas_por_matricula(id_matricula: int) -> list[dict]:
    return matricula_beca_repository.obtener_por_matricula(id_matricula)
