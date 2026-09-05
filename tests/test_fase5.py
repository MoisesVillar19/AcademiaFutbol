"""Tests de Fase 5: backup automatico (RN-030), cuotas recurrentes (RN-014) y auditoria."""
from services import backup_service, configuracion_service
from repositories import cuota_repository


def _parchear_create_backup(monkeypatch):
    """Sustituye la copia fisica por un marcador para no depender del archivo real."""
    llamadas = {}

    def fake_create_backup(custom_path=None):
        import os
        os.makedirs(custom_path or ".", exist_ok=True)
        ruta = os.path.join(custom_path or ".", "academia_test.db")
        with open(ruta, "w", encoding="utf-8") as f:
            f.write("backup-demo")
        llamadas["custom_path"] = custom_path
        return ruta

    monkeypatch.setattr(backup_service, "create_backup", fake_create_backup)
    return llamadas


class TestBackupService:

    def test_crear_backup_manual_en_ruta_configurada(self, tmp_path, monkeypatch):
        ruta_rel = str(tmp_path / "respaldos")
        configuracion_service.actualizar_configuracion({"ruta_backup": ruta_rel})

        exito, msg, ruta = backup_service.crear_backup(id_usuario=1)
        assert exito is True, msg
        assert ruta is not None

    def test_verificar_automatico_deshabilitado(self, tmp_path):
        configuracion_service.actualizar_configuracion({
            "backup_automatico": 0,
            "ruta_backup": str(tmp_path),
        })
        exito, msg = backup_service.verificar_backup_automatico()
        assert exito is False
        assert "deshabilitado" in msg.lower()

    def test_verificar_automatico_crea_si_nunca_hubo(self, tmp_path, monkeypatch):
        configuracion_service.actualizar_configuracion({
            "backup_automatico": 1,
            "frecuencia_backup": 7,
            "ruta_backup": str(tmp_path),
        })
        _parchear_create_backup(monkeypatch)

        exito, msg = backup_service.verificar_backup_automatico()
        assert exito is True, msg

    def test_frecuencia_respetada_con_backup_reciente(self, tmp_path, monkeypatch):
        configuracion_service.actualizar_configuracion({
            "backup_automatico": 1,
            "frecuencia_backup": 7,
            "ruta_backup": str(tmp_path),
        })
        monkeypatch.setattr(backup_service, "dias_desde_ultimo_backup", lambda: 2.0)
        exito, msg = backup_service.verificar_backup_automatico()
        assert exito is False
        assert "2.0" in msg or "frecuencia" in msg.lower()

    def test_frecuencia_vencida_dispara_creacion(self, tmp_path, monkeypatch):
        configuracion_service.actualizar_configuracion({
            "backup_automatico": 1,
            "frecuencia_backup": 7,
            "ruta_backup": str(tmp_path),
        })
        monkeypatch.setattr(backup_service, "dias_desde_ultimo_backup", lambda: 9.0)
        llamadas = _parchear_create_backup(monkeypatch)

        exito, msg = backup_service.verificar_backup_automatico()
        assert exito is True
        # La copia debe ir a la carpeta configurada en CONFIGURACION.ruta_backup
        assert llamadas.get("custom_path") == str(tmp_path)

    def test_ruta_absoluta_se_respeta(self, tmp_path):
        from utils.dates import get_today
        configuracion_service.actualizar_configuracion({"ruta_backup": str(tmp_path)})
        assert backup_service._resolver_ruta_backup() == str(tmp_path)


class TestCuotasRecurrentes:

    def test_pagar_cuota_genera_siguiente_mes(self, crear_matricula):
        ids = crear_matricula(monto_pactado=150.0)

        from database.connection import execute_query
        execute_query(
            "UPDATE cuota SET periodo = '2031-01', fecha_vencimiento = '2031-01-15' WHERE id_cuota = ?",
            (ids["id_cuota"],),
        )

        exito, msg = __import__("services.cuota_service", fromlist=["x"]).actualizar_pago(
            ids["id_cuota"], 150.0
        )
        assert exito is True

        cuotas = cuota_repository.obtener_por_matricula(ids["id_matricula"])
        periodos = [c["periodo"] for c in cuotas]
        assert "2031-01" in periodos
        assert "2031-02" in periodos

        siguiente = next(c for c in cuotas if c["periodo"] == "2031-02")
        assert siguiente["estado"] == "PENDIENTE"
        assert siguiente["monto_total"] == 150.0

    def test_pago_parcial_no_genera_cuota_nueva(self, crear_matricula):
        ids = crear_matricula(monto_pactado=200.0)
        from services import cuota_service
        cuota_service.actualizar_pago(ids["id_cuota"], 50.0)

        cuotas = cuota_repository.obtener_por_matricula(ids["id_matricula"])
        assert len(cuotas) == 1

    def test_base_sin_mora_al_recurrente(self, crear_matricula):
        """La cuota recurrente usa el monto base sin incluir la mora pagada."""
        ids = crear_matricula(monto_pactado=100.0)
        from models.cuota import Cuota
        from services import cuota_service
        from database.connection import execute_query

        cuota_repository.actualizar(Cuota(
            id_cuota=ids["id_cuota"],
            id_matricula=ids["id_matricula"],
            periodo="2031-03",
            fecha_vencimiento="2031-03-15",
            monto_total=115.0,
            monto_mora=15.0,
            saldo=115.0,
            estado="PENDIENTE",
        ))

        exito, _ = cuota_service.actualizar_pago(ids["id_cuota"], 115.0)
        assert exito

        siguiente = [c for c in cuota_repository.obtener_por_matricula(ids["id_matricula"])
                     if c["periodo"] == "2031-04"]
        assert len(siguiente) == 1
        assert siguiente[0]["monto_total"] == 100.0


class TestAuditoriaAmpliada:

    def test_editar_beca_registra_update(self, usuario_admin):
        from services import beca_service
        _, _, id_beca = beca_service.crear_beca({
            "nombre": "BecaEdit", "tipo": "PORCENTAJE", "valor": 10,
        })
        beca_service.editar_beca(id_beca, {"valor": 20})

        logs = __import__("services.auditoria_service", fromlist=["x"]).obtener_logs_por_tabla("beca")
        assert any(l["accion"] == "UPDATE" for l in logs)

    def test_editar_producto_registra_update(self, usuario_admin):
        from services import inventario_service
        _, _, id_cat = inventario_service.crear_categoria({"nombre": "CatAudProd"})
        inventario_service.crear_producto({
            "id_categoria_producto": id_cat, "nombre": "ProdAud",
        })
        prod = next(p for p in inventario_service.listar_productos() if p["nombre"] == "ProdAud")
        inventario_service.editar_producto(prod["id_producto"], {"precio": 99.9})

        logs = __import__("services.auditoria_service", fromlist=["x"]).obtener_logs_por_tabla("producto")
        assert any(l["accion"] == "UPDATE" for l in logs)

    def test_actualizar_configuracion_registra_update(self, usuario_admin):
        configuracion_service.actualizar_configuracion({"dias_por_vencer": 5})

        logs = __import__("services.auditoria_service", fromlist=["x"]).obtener_logs_por_tabla("configuracion")
        assert any(l["accion"] == "UPDATE" for l in logs)
