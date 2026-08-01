from repositories import matricula_repository, matricula_beca_repository, estudiante_repository
from models.matricula import Matricula
from services import auditoria_service, cuota_service, beca_service
from utils.dates import get_today
from utils.logger import logger


def crear_matricula(data: dict) -> tuple[bool, str, int | None]:
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

    matricula = Matricula(
        id_estudiante=id_estudiante,
        id_tarifa=id_tarifa,
        monto_pactado=monto_pactado,
        fecha_inicio=data.get("fecha_inicio", get_today()),
        dia_vencimiento=dia_vencimiento,
        estado="ACTIVO",
    )
    id_matricula = matricula_repository.insertar(matricula)

    tarifa = cuota_service.obtener_cuotas_por_matricula(0)

    from repositories import tarifa_repository
    tarifa_data = tarifa_repository.obtener_por_id(id_tarifa)
    monto_base = monto_pactado if monto_pactado else tarifa_data["monto"]

    becas_asignadas = data.get("becas", [])
    if becas_asignadas:
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

    cuota_service.generar_siguiente_cuota(
        id_matricula=id_matricula,
        monto_base=monto_base,
        dia_vencimiento=dia_vencimiento,
    )

    if estudiante["estado"] == "REINGRESANTE":
        from repositories import estudiante_repository as er
        er.cambiar_estado(id_estudiante, "ACTIVO")

    auditoria_service.registrar_insert(
        id_usuario=1,
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

    matricula_beca_repository.insertar(id_matricula, id_beca, observacion)
    return True, "Beca asignada correctamente"


def desasignar_beca(id_matricula: int, id_beca: int) -> tuple[bool, str]:
    matricula_beca_repository.eliminar(id_matricula, id_beca)
    return True, "Beca desasignada correctamente"


def obtener_becas_por_matricula(id_matricula: int) -> list[dict]:
    return matricula_beca_repository.obtener_por_matricula(id_matricula)
