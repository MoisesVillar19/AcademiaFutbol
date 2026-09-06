# Plan de Acción — Cierre Pendientes Sistema Local (v1.3 → v1.5)
> **Fecha:** 2026-09-06 · **Estado:** Sistema local bien encaminado (7.5/10) para 1 academia, 1 sede, OneDrive central. Pendientes son mejoras que el negocio sí requiere (no SaaS). Este plan los deja documentados, trazables y listos para implementar en 5–7 días sin romper `OneDrive\Academia\academia.db`.

> **Principio:** Todo sigue **flexible sin código** (`CONFIGURACION` + `tipo_uniforme/talla` seed) y **3 clics** si `1 almacén`.

---

## 0. Resumen ejecutivo

| Área pedida | Estado actual | Qué falta para “bien esperado” local | Esfuerzo | Archivos clave |
|---|---|---|---|---|
| **Reportes inventario** | `reporte_inventario` 8 cols + `stock_bajo_uniformes` 4 cols filtrado pero confundido (`stock_bajo_uniformes` incluye todo, no solo uniformes) + sin `valorizado` | Opción clara **Inventario completo + Valorizado** + filtro `tipo_uniforme/talla/almacén` + `AutoFilter` + `TOTAL` negrita | **M** 0.5d | `reporte_service:162`, `inventario_view:30`, `producto_repository:47` |
| **Comprobantes egreso** | `egreso` sin `comprobante_path` | Subir `jpg/png/pdf ≤5MB` → `OneDrive\Academia\comprobantes\EG-{recibo}.jpg` + thumb + `LOG` | **S** 0.5d | `egreso:225`, `egreso_service:10`, `egreso_view` |
| **Dashboards frágil** | `dashboard_service:35` `try/except` pone `0` silencioso; `nuevos LIKE` frágil; sin `MoM` | `neto` con `try` logueado, `nuevos` por `matricula_beca` + `estado`, `MoM` comparativo, filtro fecha | **M** 0.5d | `dashboard_service:7`, `dashboard_view:62` |
| **Reportes PDF demo** | 9 Excel `openpyxl` `header #4472C4` sin PDF | Demo PDF `reportlab` con logo, header, tabla, totales, firma (aunque sin estilo final) | **M** 0.5d | `utils/excel_exporter:12` + `reportlab` 5.0 ya en `AcademiaFutbol.spec:24` |
| **Backup restore** | `backup.py:7` `copy2` + `auto 6h` `main:276` + OneDrive, **sin UI restore** | `Configuración → Respaldo` lista `glob academia_*.db` + `Restaurar 1-click con PIN` + `close_connection` + preview | **M** 0.5d | `database/restore.py:7`, `services/backup_service:10` |
| **Roles/Usuarios** | `ADMIN/SECRETARIA` binario `constants:98` | Matriz 4 roles + 6 permisos módulo (ej. SECRETARIA ve Dashboard/Reportes pero no Egresos/Config) | **M** 1d | `auth_service:79`, `main:240`, `usuario_view` |

**Orden recomendado (ROI):** `1. Comprobantes egreso` (S, control) → `2. Reporte inventario valorizado` (M) → `3. PDF demo` (M) → `4. Dashboard robusto` (M) → `5. Backup restore` (M) → `6. Roles granular` (M, deja para v1.5 si urge).

---

## 1. Reportes de Inventario — opción valorizado y clara

### 1.1 Estado
- **Existe:** `reporte_inventario` 8 cols `codigo/nombre/categoria/tipo_uso/stock_actual/minimo/precio/estado` `reporte_service:162-195` + `stock_bajo_uniformes` 4 cols `codigo/nombre/stock/minimo` `reporte_view:152-167` (filtra `stock <= minimo` pero **miente** “uniformes” porque filtra todo).
- **Falta:** `stock * precio_venta` (valorizado), `tipo_uniforme`, `talla`, `almacén`, `proveedor`, `fecha_caducidad`, `AutoFilter`, `TOTAL` valorizado, `freeze_panes`.

### 1.2 Objetivo
Un solo reporte **Inventario + Valorizado** con opción filtro `Todos / Solo bajo stock / Solo uniformes / Por almacén` y columnas `SKU, Nombre, Categoría, Tipo uniform, Talla, Almacén, Stock, Mínimo, Compra, Venta, Ganancia, Valorizado (stock×venta), Estado, Proveedor, Caducidad`.

### 1.3 Solución detallada

**DDL:** ya existe `producto.precio_compra/venta` `create_db:175-176`, `talla` `214`, `producto_variante` `237`, `stock_almacen` `247`, `lote` `257`. Solo añadir índice `producto(id_tipo_uniforme, activo)` si falta.

**Service `reporte_service.py`:**
```python
def reporte_inventario_valorizado(ruta, filtro="todos", id_almacen=None):
    # filtro: todos | bajo | uniformes | almacen
    # query: LEFT JOIN tipo_uniforme + LEFT JOIN talla via producto_variante + LEFT JOIN stock_almacen + lote
    # para cada fila: valorizado = stock_actual * coalesce(precio_venta, precio)
    # datos = [{sku, nombre, ..., compra, venta, ganancia=venta-compra, valorizado, estado, proveedor, caducidad}]
    # columnas 13 + fila TOTAL sum(valorizado) bold + fill #E2EFDA
    # exportar_a_excel con AutoFilter + freeze_panes="A5" + number_format '"S/" #,##0.00'
```

**View `reporte_view.py:128`:**
- Añadir `id: inventario_valorizado` a `listar_reportes`
- Diálogo con `Combo filtro [Todos, Bajo stock, Solo uniformes, Por almacén]` + si `Por almacén` muestra `Combo almacén` (`almacen_repository.obtener_todos()`)
- `_ejecutar_exportacion` nuevo `elif reporte_id == "inventario_valorizado": reporte_service.reporte_inventario_valorizado(...)`

**Controller `reporte_controller.py:25`:** `def reporte_inventario_valorizado(...): return reporte_service...`

**Criterios:**
- [ ] Con `filtro=bajo` solo filas `stock <= minimo`
- [ ] Con `uniformes` solo `id_tipo_uniforme IS NOT NULL`
- [ ] `Valorizado` = `round(stock * precio_venta,2)` y `TOTAL` suma negrita
- [ ] Excel con `AutoFilter` y `freeze_panes A5`

**Esfuerzo:** **M 0.5d** · Archivos: `reporte_service`, `reporte_view`, `reporte_controller`, `producto_repository` (agregar `LEFT JOIN`).

---

## 2. Comprobantes de Egreso

### 2.1 Estado
`egreso:225` `concepto/monto/fecha/responsable/observacion/activo` **sin** `comprobante_path`. `egreso_service:10` valida `concepto IN 5` y `monto>0` pero no archivo. `egreso_view:30` form `Concepto, Monto, Fecha, Responsable, Observación` sin upload. Auditoría `24` no muestra comprobante.

### 2.2 Objetivo
Igual que `pago_view:100` `YAPE` exige `jpg/png ≤5MB` → `OneDrive\Academia\comprobantes\EG-{numero_recibo o id}.jpg` + thumb 70 + `os.startfile` + `LOG` con `comprobante_path`.

### 2.3 Solución

**DDL `create_db.py:225`:**
```sql
ALTER TABLE egreso ADD COLUMN comprobante_path TEXT;
```

**Model `models/egreso.py:5`:** `comprobante_path: str | None = None`

**Repository `repositories/egreso_repository.py:5`:**
```python
def insertar(...) VALUES (..., comprobante_path) # 7 cols + comprobante
def obtener_por_id JOIN ... # incluir comprobante_path
```

**Service `services/egreso_service.py:10`:**
```python
comprobante = data.get("comprobante_path")
if concepto in ("CAMPEONATO_FIJO","ARBITRAJE","VIATICOS") and not comprobante:
    logger.warning(f"Egreso {concepto} sin comprobante")
# si comprobante: validar ext jpg/png/pdf y size ≤5MB, copiar a COMPROBANTES_DIR
```

**View `views/egresos/egreso_view.py:30`:**
- `btn_comprobante` `📎 Seleccionar comprobante` + `label_comprobante` + `label_preview 70` thumb `PIL` (igual que `pago_view:100`)
- Card `egreso` muestra `📎 nombre.jpg (clic)` si existe
- `listar_egresos` tabla + columna `Comprobante`

**Migrar:** `create_db.py:302` `_migrar _obtener_columnas(egreso) if "comprobante_path" not in ... ALTER`.

**Criterios:**
- [ ] Subir `egreso` con `PROFESOR 200` + `comprobante.jpg` → `egreso.comprobante_path` guarda `OneDrive\...\EG-*.jpg` y thumb visible
- [ ] Sin comprobante en `VIATICOS` solo `warning` no bloquea (flexible)
- [ ] `LOG egreso` incluye `comprobante_path`

**Esfuerzo:** **S 0.5d**

---

## 3. Dashboards frágil → robusto

### 3.1 Estado
`dashboard_service.py:7` `obtener_indicadores()`:
```python
try: ingresos_ventas_mes = venta.sumar... except: ingresos_ventas_mes=0  # silencioso
nuevos_mes = SELECT ... WHERE fecha_ingreso LIKE 'YYYY-MM%'  # frágil reingreso
neto_mes = total_ingresos - egresos  # si try falla, 0-0=0
```
`dashboard_view.py:62` 5 filas 15 cards `Alumnos/Vencidas/Pagos/Ingresos/Ventas/Egresos/Neto/Nuevos` bien, pero `Ingresos vs Egresos` sin `MoM`.

### 3.2 Objetivo
- `try` con `logger.warning` no `0` silencioso
- `nuevos` = `COUNT(DISTINCT id_estudiante) WHERE primera_matricula.fecha_inicio BETWEEN` (no `estudiante.fecha_ingreso LIKE`), `antiguos = matriculas_activas - nuevos` consistente
- `neto` con `try` logueado y `None` si falla (no `0`)
- Añadir `MoM` `Ingresos_mes_actual vs mes_anterior %` y filtro `DatePicker inicio/fin` en header dashboard (no solo `Actualizar`)

### 3.3 Solución

**Service `dashboard_service.py:7`:**
```python
try:
    ingresos_ventas_mes = venta_repository.sumar_por_periodo(...)
except Exception as e:
    logger.warning(f"Dashboard ingresos_ventas falló: {e}")
    ingresos_ventas_mes = None  # no 0
# nuevos
nuevos_mes = fetch_one("SELECT COUNT(DISTINCT m.id_estudiante) FROM matricula m WHERE m.fecha_inicio BETWEEN ? AND ? AND m.estado='ACTIVO'", (ini, fin))["count"]
# MoM
ingresos_mes_anterior = pago_repository.sumar... (mes anterior)
mom = (ingresos_mes - ingresos_mes_anterior)/ingresos_mes_anterior*100 if ingresos_mes_anterior else 0
```

**View `dashboard_view.py:20`:**
- Header añade `DatePicker inicio/fin` + `Aplicar` → recarga `obtener_indicadores(fecha_inicio, fecha_fin)` (opcional)
- Card `Neto Mes` muestra `S/ -` y tooltip `No se pudo calcular` si `None`
- `Nuevos/Antiguos` usa nuevo cálculo

**Criterios:**
- [ ] `Dashboard` con `OneDrive` sin `venta` tabla no pone `0` silencioso sino `—`
- [ ] `Nuevos` no cuenta `REINGRESANTE` como nuevo
- [ ] `MoM` muestra `+12% vs mes anterior` con flecha

**Esfuerzo:** **M 0.5d**

---

## 4. Reportes PDF demo (aunque sin estilo final)

### 4.1 Estado
9 Excel `openpyxl` `header #4472C4` bien, 0 PDF. `reportlab==5.0.0` ya en `requirements` y `AcademiaFutbol.spec:24` pero no se usa. Mercado pide PDF con logo para entregar.

### 4.2 Objetivo demo (suficiente)
- Mismo diálogo `reporte_view:57` `Exportar` → `filedialog` `*.pdf` + `*.xlsx` (combo `Tipo: Excel/PDF`)
- `utils/pdf_exporter.py` nuevo con `reportlab` `SimpleDocTemplate` + `Table` + `Paragraph` + `Image logo_roncalli.png` + `TableStyle` `BACKGROUND #4472C4` + `TOTAL` negrita + `footer` `nombre_academia + fecha`
- `reporte_service.py` duplica cada `reporte_*` con `*_pdf` que llama `exportar_a_pdf`

### 4.3 Solución mínima demo

```python
# utils/pdf_exporter.py
def exportar_a_pdf(datos, columnas, titulo, ruta):
    doc = SimpleDocTemplate(ruta, pagesize=A4)
    styles = getSampleStyleSheet()
    data = [[h for _,h in columnas]] + [[row[k] for k,_ in columnas] for row in datos]
    t = Table(data, repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#4472C4')), ('TEXTCOLOR',(0,0),(-1,0),colors.white), ('ALIGN',(0,0),(-1,-1),'CENTER'), ('GRID',(0,0),(-1,-1),0.5,colors.black)]))
```

**View:** `reporte_view:94` `filetypes [("Excel","*.xlsx"),("PDF","*.pdf")]` + `if ruta.endswith(".pdf"): reporte_service.reporte_*_pdf else excel`

**Criterios:**
- [ ] Exportar `Morosos.pdf` abre con `Academia Deportiva` header + tabla + `TOTAL` + fecha
- [ ] `Ingresos vs Egresos.pdf` con `logo_roncalli.png` 40px

**Esfuerzo:** **M 0.5d** (1 util + 9 wrappers)

---

## 5. Backup → Restore UI y demás

### 5.1 Estado
`backup.py:7` `copy2` + `backup_service:10` auto 6h `main:276` + manual `configuracion_controller:39` OK. `restore.py:7` solo CLI `close_connection + copy2`, **sin UI**, sin lista, sin verificación, sin rotación, sin cifrado.

### 5.2 Objetivo
`Configuración → Respaldo` ya tiene `Backup` `frecuencia/ruta/correo` + botón `Respaldo manual`. Añadir:

- Lista `OneDrive\BackupsAcademia\academia_*.db` con `fecha, tamaño, SHA256 (4 primeros)`
- `Restaurar` `1-click` con `PIN` `verify_password(pin, pin_hash)` + `close_connection` + `copy2` + `messagebox` `Reinicie`
- `Verificar` botón `checksum` + `Rotación` `borrar >30 días` (config `dias_retencion 30`)

### 5.3 Solución

**Service `services/backup_service.py`:**
```python
def listar_backups(): glob + os.path.getmtime + hashlib.sha256
def verificar_backup(ruta): sha256
def rotar_backups(dias=30): borrar si mtime < now-30d
def restaurar_backup(ruta, pin): verify_password(pin, pin_hash) + close_connection + copy2
```

**View `views/configuracion/configuracion_view.py:98` Sec.5:**
- `Listbox` backups `ScrollableFrame` con `Restaurar` por fila + `Verificar` + `Rotar`
- Dialog `PIN` antes de restaurar

**Controller `configuracion_controller.py:39`:** `listar_backups`, `restaurar_backup(ruta, pin)`, `verificar_backup`

**Criterios:**
- [ ] Lista muestra `3` backups con `2026-09-05 22:00, 12MB, a3f4...`
- [ ] `Restaurar` pide `PIN` + `¿Seguro?` + `Reinicie app` y DB vuelve
- [ ] `Rotar` borra `>30d` y `LOG` `ROTACION`

**Esfuerzo:** **M 0.5d**

---

## 6. Roles/Usuarios granular

### 6.1 Estado
`ADMIN(7 perms)/SECRETARIA(7)` `AGENTS.md` `constants:98` `ROLE_ADMIN/SECRETARIA` + gate `main:240` `if es_admin(): Egresos/Usuarios...` + `usuario_service:9` `crear_usuario` `hash` + `auth:79` `es_admin`. Binario, no matriz.

### 6.2 Objetivo (sin romper local)
Matriz 4 roles × 6 módulos (configurable sin código, como precios):

| Rol | Dashboard | Estudiantes/Matrículas/Pagos/Ventas/Inventario | Reportes | Egresos | Config/Tarifas/Becas | Usuarios/Auditoría/Restore |
|---|---|---|---|---|---|---|
| ADMIN | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| SECRETARIA | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| CAJA | ✅ | ✅ Pagos/Ventas solo | ✅ | ❌ | ❌ | ❌ |
| INVENTARIO | ✅ | ✅ Inventario solo | ✅ Inventario | ❌ | ❌ | ❌ |

Si `COUNT(rol)!=2` UI oculta `COUNT>2` muestra `SECRETARIA` como `CAJA` etc.

### 6.3 Solución

**DDL:** `ALTER TABLE usuario ADD COLUMN permisos TEXT DEFAULT '[]'` JSON `["pagos","ventas"]` o nueva `rol_permisos` tabla; o simple `rol` enum `ADMIN/SECRETARIA/CAJA/INVENTARIO` + `CHECK`.

**Service `auth_service:79` `tiene_permiso(modulo)`:** `if es_admin: True else: modulo in usuario["permisos"]`

**Controller/View:** `main:240` `if tiene_permiso("egresos"): mostrar Egresos` (no solo `es_admin`)

**View `usuarios/usuario_view.py:7`:** `Combo rol` con 4 valores + `Checklist permisos` (si `SECRETARIA` tildar `Pagos, Ventas`).

**Migración:** `create_db:302` `ALTER ADD COLUMN permisos` + `seed` `ADMIN [] = todos`.

**Criterios:**
- [ ] Crear `CAJA` con `permisos [pagos,ventas]` → ve `Finanzas` pero no `Egresos/Config`
- [ ] `SECRETARIA` no ve `Egresos` (antes sí vía `Finanzas` si `es_admin` falso, ahora `CAJA` tampoco)

**Esfuerzo:** **M 1d** (DDL + service + view + seed)

---

## 7. Plan de entrega (5 días, sin romper OneDrive)

| Día | Entregable | `file:line` | Test |
|---|---|---|---|
| 1 | **Comprobantes egreso** + **Inventario valorizado** | `egreso:225`, `reporte_service:162` | `test_inventario_escalable` + `test_egreso_comprobante` |
| 2 | **Dashboard robusto** `neto` + `nuevos` + `MoM` + filtro fecha | `dashboard_service:7`, `dashboard_view:62` | `test_dashboard` |
| 3 | **PDF demo** `utils/pdf_exporter` + 9 `*_pdf` | `reporte_view:94` | Exportar `Morosos.pdf` abre |
| 4 | **Backup restore UI** + rotación + verificación | `backup_service:10`, `configuracion_view:98` | Lista `3` backups, `Restaurar` con `PIN` |
| 5 | **Roles granular** 4 roles + matriz | `usuario:9`, `auth:79`, `main:240` | `CAJA` ve solo `Pagos/Ventas` |

**Documentación:** Cada sprint actualiza `docs/desarrollo/plan_deuda_tecnica.md` + `docs/README.md` índice.

**No romper:** `dist` sin `academia.db`, `updater` excluye `database/*.db` `config.ini` `updater:158`, `OneDrive` `WAL` intacto.

---
> **Siguiente paso:** Priorizo `1. Egreso comprobante` (S) → `2. Inventario valorizado` (M) si estás de acuerdo.
