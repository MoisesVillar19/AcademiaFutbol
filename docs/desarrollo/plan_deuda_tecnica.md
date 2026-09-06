# Plan Deuda Técnica — AcademiaFutbol (v2 + vistas funcionales)

> **Fecha:** 2026-09-06 · **Estado:** Post-migración BD OneDrive + `tipo_uniforme/venta/egreso` + `config precios`. Vistas funcionales con existentes + nuevas (flexible configurable).

### 1. Deuda crítica corregida (esta iteración)

| ID | Deuda | Fix `file:line` | Verificación |
|---|---|---|---|
| D01 | `auth_service:60` fallback `else 1` | `auth_service.py:60` `id_usuario_sesion()->int|None` + `id_usuario_sesion_or_system()` con `logger.warning`, `auditoria_service:5` `or_system` | Llamadas sin sesión auditan `1` con warning; controllers que exigen login usan `strict` |
| D02 | `egreso DELETE` físico `egreso_repository:37` | `create_db.py:225` `activo INTEGER DEFAULT 1` + migración `if "activo" not in egreso`, `egreso_repository:37` `soft_delete` + `eliminar` deprecado | `RN-028` ok |
| D03 | `configuracion_service:22` no persistía `precio_*` | `configuracion_service:22` mapea 7 precios + `pin_emergencia` a `Configuracion`, `configuracion_repository:10` 7 columnas | Config 100% editable ADMIN sin código |
| D04 | `estudiante_controller:112` `Controller→Repo` | `estudiante_controller:112` delega `apoderado_service.obtener_por_persona` | Capa OK |
| D05 | `pago_view:251` `View→Service` | `pago_view:246` usa `pago_controller.obtener_cuotas_pendientes`, `pago_controller:56` nuevo wrapper | Capa OK |
| D06 | `egreso_service:20` `except:` bare | `egreso_service:20` `except (ValueError,TypeError)` + `logger.warning` | `AGENTS` ok |
| D07 | `venta_service:32` `pass` RN-042 | `venta_service:32` `logger.warning` en vez de `pass` | Trazable |

### 2. Vistas — soporte v2 (funcionales)

| Vista | Estado post-fix | Qué soporta | Falta menor (no bloquea) |
|---|---|---|---|
| **Inventario** `inventario_view.py:145` | ✅ Funcional | `tipo_uniforme` combo + `precio_compra/venta/ganancia` + card uniforme | Foto/preview (opcional) |
| **Configuración** `configuracion_view.py:54` | ✅ Funcional | 7 precios `precio_inscripcion/mensualidad/reingreso/uniforme/tasa/arbitraje/pago_profesor` + CRUD `tipo_uniforme` + `mora/días` | Validación rango precios |
| **Ventas** `views/ventas/venta_view.py:1` | ✅ Nuevo funcional | `UNIFORME/TIENDA/CAMPEONATO/INSCRIPCION`, stock check, `comprobante_path` OneDrive, `detalle_venta` | Búsqueda por tipo |
| **Egresos** `views/egresos/egreso_view.py:1` | ✅ Nuevo funcional | `PROFESOR/PERSONAL/CAMPEONATO_FIJO/ARBITRAJE/VIATICOS` + reporte `Ingresos vs Egresos` `egreso_service:44` | Filtro fecha avanzado |
| **Main** `main.py:184` | ✅ Funcional | Sidebar `🛒 Ventas` (todos) + `💸 Egresos` (ADMIN) | - |
| **Matrícula** `matricula_view.py:57` | ✅ Funcional | `diferir 0/2/3 meses` `combo_diferir` → `matricula_service:71` genera N cuotas | Fecha matrícula picker |
| **Pagos** `pago_view.py:76` | ✅ Funcional | `comprobante foto` obligatorio si `≠EFECTIVO` `RN-042` + `OneDrive\comprobantes` | Thumb preview `184` |
| **Estudiante** `estudiante_view.py` | ⚠️ Parcial funcional | `DNI/CARNET`, apoderado, `REINGRESANTE` existe | **Foto niño** `RN-041` picker `fotos/{dni}.jpg` + reingreso venta dialog (próx. sprint) |
| **Dashboard** `dashboard_view.py` | ⚠️ Parcial | `vencidas/por_vencer/pagos/stock_bajo` `RN-031` | Cards `Ventas/Egresos/Neto`, `Nuevos vs Antiguos %` (usa `venta/egreso` sum) |
| **Reportes** `reporte_view.py` | ⚠️ Parcial | 6 reportes base ok | 3 nuevos `Ingresos vs Egresos`, `Stock bajo uniformes`, `Nuevos vs Antiguos` (backend sum ya existe) |
| **Auditoría** `auditoria_view.py` | ⚠️ Parcial | Gate `ADMIN` + filtros fecha `RN-034/035` | Combo `venta/egreso/tipo_uniforme` + mostrar `valor_anterior/nuevo` fotos |

**Conclusión vistas:** Existentes no rotas; nuevas `Ventas/Egresos` funcionales; 4 vistas parciales con deuda menor no bloqueante (foto/reporte). Todas operables con lógica flexible (precios/tipos configurables sin código).

### 3. Deuda restante — plan por sprints

| Sprint | Deuda | file:line | Esfuerzo |
|---|---|---|---|
| **S1 (1d)** | `estudiante_view` foto picker `RN-041` + dialog reingreso venta `RN-044` | `estudiante_view.py:64` + `FOTOS_DIR` `constants.py:95` | M |
| **S1** | `dashboard/reportes` 3 reportes v2 + auditoría combo | `dashboard_service:7`, `reporte_view:27` | M |
| **S2 (0.5d)** | `vente TOCTOU` valida stock dentro `transaccion` + `BEGIN IMMEDIATE` | `venta_service:46` | S |
| **S2** | `helpers:16` `PRD` colisión + `logger:15` `RotatingFileHandler` OneDrive-aware | `helpers.py:16`, `logger.py:15` | S |
| **S3** | `connection.py:21` `DB_PATH` stale OneDrive lazy + `PRAGMA table_info` interpolado | `constants.py:54`, `create_db.py:341` | S |
| **S3** | `constants.py:117` `PIN` en claro → wizard env + `os.getenv` | `constants.py:117` | S |

**No bloquean release:** Todos los `RN-036..050` operan vía Services/DB aunque UI parcial.

### 4. Validación

- `py -c create_tables+seed` → `tipos 4`, `precio_inscripcion 100` ok
- `venta UNIFORME` `stock 50→49` + `egreso PROFESOR 200` + `reporte neto` ok
- `DB_PATH` `OneDrive\Academia\academia.db`, `FOTOS_DIR`/`COMPROBANTES_DIR` OneDrive `constants.py:86`
- `AcademiaFutbol.spec:104` datas `config.ini` + hiddenimports `venta/egreso/tipo_uniforme`

**Próximo paso:** Sprint S1 foto/reingreso + dashboard 3 reportes (1 día) → release `v1.1.0` funcional completo OneDrive.
