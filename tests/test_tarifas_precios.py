"""F2 v2.2: precios viven en Tarifas (categorias con tipo, campeonato por tarifa)."""
from controllers import categoria_controller, tarifa_controller, matricula_controller
from services import categoria_service, venta_service


def test_categoria_campeonato_sin_edad_ok():
    exito, msg, cid = categoria_service.crear_categoria(
        {"nombre": "Copa QA", "tipo": "CAMPEONATO"})
    assert exito is True, msg
    assert cid and cid > 0


def test_categoria_academia_sin_edad_rechazada():
    exito, msg, cid = categoria_service.crear_categoria(
        {"nombre": "SinEdad QA", "tipo": "ACADEMIA"})
    assert exito is False
    assert cid is None


def test_categoria_tipo_invalido_rechazado():
    exito, msg, cid = categoria_service.crear_categoria(
        {"nombre": "Rara QA", "tipo": "OTRO", "edad_min": 1, "edad_max": 2})
    assert exito is False


def test_migracion_seed_tarifas_desde_config():
    # la migracion corre en create_tables (fixture): categorias + 5 tarifas
    from repositories import categoria_repository, tarifa_repository
    cats = {c["nombre"]: c for c in categoria_repository.obtener_todas()}
    assert "Servicios" in cats and cats["Servicios"]["tipo"] == "SERVICIO"
    assert "Campeonatos" in cats and cats["Campeonatos"]["tipo"] == "CAMPEONATO"
    assert cats["Servicios"]["edad_min"] is None
    nombres = {(t["categoria_nombre"], t["nombre"]) for t in tarifa_repository.obtener_activas()}
    for par in [("Servicios", "Inscripción"), ("Servicios", "Reingreso"),
                ("Servicios", "Uniforme base"), ("Campeonatos", "Tasa base"),
                ("Campeonatos", "Arbitraje por equipo")]:
        assert par in nombres, par
    # idempotente: correr migracion otra vez no duplica
    from database.create_db import create_tables
    create_tables()
    nombres2 = [(t["categoria_nombre"], t["nombre"]) for t in tarifa_repository.obtener_activas()]
    for par in [("Servicios", "Inscripción"), ("Campeonatos", "Tasa base")]:
        assert nombres2.count(par) == 1, par


def test_tarifas_por_tipo():
    camp = tarifa_controller.listar_tarifas_activas(tipo="CAMPEONATO")
    assert len(camp) >= 2
    acad = tarifa_controller.listar_tarifas_activas(tipo="ACADEMIA")
    assert all(t.get("categoria_tipo") == "ACADEMIA" for t in acad)
    mat = matricula_controller.listar_tarifas_activas(tipo="ACADEMIA")
    assert all(t.get("categoria_tipo") == "ACADEMIA" for t in mat)


def test_sugerencia_edad_ignora_sin_edad():
    from services import categoria_service as cs
    exito, _, _ = cs.crear_categoria({"nombre": "Libre QA", "tipo": "SERVICIO"})
    assert exito is True
    cat = matricula_controller.obtener_tarifa_sugerida_por_edad("2018-01-01")
    assert cat is None or isinstance(cat, int)


def test_venta_campeonato_por_tarifa_sin_items(usuario_admin):
    tarifas = tarifa_controller.listar_tarifas_activas(tipo="CAMPEONATO")
    assert tarifas
    t = tarifas[0]
    exito, msg, vid = venta_service.registrar_venta({
        "id_usuario": 1, "tipo_venta": "CAMPEONATO", "metodo_pago": "EFECTIVO",
        "items": [], "id_tarifa": t["id_tarifa"], "monto_total": 123.45,
    })
    assert exito is True, msg
    from repositories import venta_repository
    v = venta_repository.obtener_por_id(vid)
    assert v["monto_total"] == 123.45
    assert v["id_tarifa"] == t["id_tarifa"]


def test_venta_campeonato_sin_monto_rechazada(usuario_admin):
    exito, msg, vid = venta_service.registrar_venta({
        "id_usuario": 1, "tipo_venta": "CAMPEONATO", "metodo_pago": "EFECTIVO",
        "items": [],
    })
    assert exito is False
    assert vid is None


def test_venta_normal_sigue_exigiendo_items(usuario_admin):
    exito, msg, vid = venta_service.registrar_venta({
        "id_usuario": 1, "tipo_venta": "TIENDA", "metodo_pago": "EFECTIVO",
        "items": [], "monto_total": 50,
    })
    assert exito is False
    assert vid is None
