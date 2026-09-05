"""Tests de cobertura de auditoria (RN-032): operaciones criticas escriben LOG."""
import pytest
from services import (
    auditoria_service,
    beca_service,
    categoria_service,
    cuota_service,
    inventario_service,
    pago_service,
    usuario_service,
)
from repositories import log_repository


def _hay_log(tabla, accion=None):
    logs = auditoria_service.obtener_logs_por_tabla(tabla, limit=500)
    return any(
        l["tabla_afectada"] == tabla and (accion is None or l["accion"] == accion)
        for l in logs
    )


def test_login_registra_log(usuario_admin):
    assert _hay_log("usuario", "LOGIN")


def test_crear_usuario_registra_log(usuario_admin):
    usuario_service.crear_usuario(
        {"dni": "56565656", "nombres": "Log", "apellidos": "Test"},
        "user_log", "SECRETARIA",
    )
    assert _hay_log("usuario", "INSERT")


def test_desactivar_usuario_registra_desactivacion(usuario_admin):
    _, _, id_u = usuario_service.crear_usuario(
        {"dni": "57575757", "nombres": "Off", "apellidos": "Test"},
        "user_off", "SECRETARIA",
    )
    usuario_service.desactivar_usuario(id_u)
    assert _hay_log("usuario", "DESACTIVACION")


def test_crear_beca_y_asignar_registran_log(usuario_admin, obtener_tarifa, crear_matricula):
    _, msg, id_beca = beca_service.crear_beca({
        "nombre": "Beca Log", "tipo": "PORCENTAJE", "valor": 10,
    })
    assert _hay_log("beca", "INSERT")

    ids = crear_matricula()
    matricula_service_asignar(ids, id_beca)
    assert _hay_log("matricula_beca", "INSERT")


def matricula_service_asignar(ids, id_beca):
    from services import matricula_service
    matricula_service.asignar_beca(ids["id_matricula"], id_beca)


def test_actualizar_pago_registra_update(usuario_admin, crear_matricula):
    ids = crear_matricula()
    cuota_service.actualizar_pago(ids["id_cuota"], 50.0)
    assert _hay_log("cuota", "UPDATE")


def test_movimiento_inventario_registra_log(usuario_admin):
    exito, msg, id_cat = inventario_service.crear_categoria({"nombre": "CatLog"})
    inventario_service.crear_producto({
        "id_categoria_producto": id_cat, "nombre": "ProdLog",
    })
    prod = next(p for p in inventario_service.listar_productos() if p["nombre"] == "ProdLog")
    inventario_service.registrar_movimiento({
        "id_producto": prod["id_producto"],
        "tipo_movimiento": "ENTRADA", "cantidad": 4,
    })

    assert _hay_log("categoria_producto", "INSERT")
    assert _hay_log("producto", "INSERT")
    assert _hay_log("movimiento_inventario", "INSERT")


def test_desactivar_categoria_registra_desactivacion(usuario_admin):
    categoria_service.crear_categoria({"nombre": "CatDesact", "edad_min": 3, "edad_max": 5})
    cat = next(c for c in categoria_service.listar_todas_las_categorias()
               if c["nombre"] == "CatDesact")
    categoria_service.desactivar_categoria(cat["id_categoria"])
    assert _hay_log("categoria", "DESACTIVACION")


def test_pago_registra_insert(usuario_admin, crear_matricula):
    ids = crear_matricula(monto_pactado=100.0)
    pago_service.registrar_pago({
        "id_usuario": 1, "id_cuota": ids["id_cuota"],
        "monto_pagado": 50.0, "metodo_pago": "EFECTIVO",
    })
    assert _hay_log("pago", "INSERT")


def test_logs_solo_lectura_sin_metodos_mutadores():
    """El LOG es inmutable: no deben existir funciones de update/delete."""
    import repositories.log_repository as lr
    funciones_publicas = [f for f in dir(lr) if callable(getattr(lr, f))
                          and not f.startswith("_")]
    prohibidas = [f for f in funciones_publicas
                  if f.startswith(("actualizar", "eliminar", "delete", "update"))]
    assert prohibidas == []
