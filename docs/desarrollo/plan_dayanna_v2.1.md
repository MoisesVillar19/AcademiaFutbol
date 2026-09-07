# Plan Dayanna v2.1 — Revisión + Nuevos Requerimientos Documentados

> **Fecha:** 2026-09-06 · **Estado:** Documentado, pendiente implementación
> **Origen:** `DAYANNA_REVISION.md` v2.1 + Plan de Acción 5 Fases (usuario 2026-09-06) + 3 aclaraciones
> **Fuente de verdad:** `AGENTS.md` > `sistema/reglas_negocio.md` > `sistema/arquitectura_bd.md` > `sistema/diccionario_datos.md`
> **Objetivo:** Dejar diseñado sin redundancia cómo se implementará cada item para luego ejecutar en lotes sin conflicto.

---

## 1) Respuestas a las 3 aclaraciones

### 1.1 ¿Dónde va "Estudiante Nuevo"? — En registro de estudiante
- **Decisión:** Checkbox `¿Es estudiante nuevo?` en `views/estudiantes/estudiante_view.py` formulario `+ Nuevo / Editar`.
- **Motivo:** Los alumnos existentes se cargarán manualmente al inicio. Solo los realmente nuevos se marcan `es_nuevo=1` en ese momento. No va en `Matrículas`, va en `Estudiante`.
- **Comportamiento:**
  - Al crear estudiante: checkbox editable, default `0` (no marcado) para cargas masivas de existentes; marcar `1` solo si es alta nueva real.
  - Una vez guardado, campo queda bloqueado (disabled) para siempre en ese `id_estudiante`. Editar no lo puede cambiar. Así se cumple "única vez en el ciclo de vida".
  - `services/estudiante_service.py:crear_estudiante()` valida y persiste; `editar_estudiante()` ignora si intenta cambiar `es_nuevo`.
  - Diferenciación visual: `views/estudiantes/estudiante_view.py` filtro `Activos` incluye `REINGRESANTE` (parche fase 3) y lista muestra badge `NUEVO` si `es_nuevo=1`.
- **RN nuevo:** `RN-051` (ver §5).

### 1.2 Precios flexibles — qué es lo más recomendable para no generar redundancia
- **Problema:** Hoy hay dos fuentes de precio: `configuracion.precio_inscripcion/mensualidad/reingreso/uniforme` (fila única) y `tarifa.monto` por categoría. Añadir "Precios flexibles con títulos + ítems incluidos" encima generaría triple fuente y conflictos (¿qué precio manda?).
- **Recomendación (aprobada para v2.1): Coexistencia con jerarquía clara + catálogo único de conceptos, sin duplicar columnas.**
  - **Mantener** `configuracion.precio_*` como **defaults heredados / fallback simple**. No borrar. Sirven para matrícula rápida sin bundle y para compatibilidad con BD existente y `seed.py`.
  - **No crear** otra tabla `precio_flexible` paralela a `tarifa`. En su lugar crear **un único catálogo** `concepto_cobro` (nombre genérico para no colisionar con `tarifa`):
    ```sql
    concepto_cobro(id_concepto PK, nombre TEXT UNIQUE, tipo TEXT CHECK('INSCRIPCION','MENSUALIDAD','REINGRESO','PROMOCION','CAMPEONATO','OTRO'), monto REAL NOT NULL, descripcion TEXT, activo INTEGER DEFAULT 1)
    concepto_item(id_item PK, id_concepto FK, id_producto FK, cantidad INTEGER DEFAULT 1)
    ```
  - **Regla de precedencia al calcular importe de matrícula:**
    1. Si se elige un `concepto_cobro` en el form `Matrículas → Registrar` → `monto_base = concepto_cobro.monto` (ignora `tarifa` y `configuracion` para ese cobro).
    2. Si no se elige concepto → `monto_base = monto_pactado ?? tarifa.monto ?? configuracion.precio_*` (según tipo de operación: inscripción usa `precio_inscripcion`, mensualidad `precio_mensualidad`, reingreso `precio_reingreso`).
  - **Ítems incluidos:** Cada `concepto_cobro` puede tener 0..N `concepto_item` (productos del inventario). Al matricular con un concepto que tiene items, `services/matricula_service.py:crear_matricula()` itera `concepto_item` y crea `venta`/`movimiento_inventario` por cada producto (mismo flujo atomico `transaccion()` que hoy usa `productos` en `matricula_service.py:98`). Si el concepto es "Matrícula Promocional S/150 incluye Camiseta + Media" → descuenta stock de ambos.
  - **Sin redundancia:** No se duplica `precio_uniforme` en `configuracion` y en `producto.precio_venta`; `producto.precio_venta` manda para uniformes. `concepto_cobro.monto` es el precio del bundle, no la suma de productos (puede ser promo).
  - **Migración suave:** `configuracion.precio_*` sigue funcionando si no hay concepto seleccionado. A futuro se puede deprecar sin romper datos históricos (matrículas ya guardadas tienen `monto_pactado` congelado).
  - **UI:** `views/configuracion/configuracion_view.py:2.Precios` añade sub-sección `Conceptos flexibles → + Nuevo concepto` con multiselector de productos (checklist). `views/matriculas/matricula_view.py` añade `ComboBox Concepto (opcional)` arriba de `Productos adicionales`. Ayuda `↳` explica precedencia.

### 1.3 Dar más libertad a la secretaria
- **Decisión:** Secretaria pasa de rol casi solo lectura en finanzas a **operativa completa**, Admin retiene lo crítico.
- **Matriz nueva (actualiza `AGENTS.md` y `arquitectura_bd.md#Seguridad`):**

| Módulo | Secretaria | Admin | Archivo gate |
|---|---|---|---|
| Estudiantes/Apoderados/Matrículas/Pagos/Ventas/Inventario/Dashboard/Reportes | ✅ CRUD | ✅ | `services/*` sin gate |
| Egresos: crear/editar | ✅ | ✅ | `services/egreso_service.py` + `controllers/egreso_controller.py:14` quitar `ADMIN only` en `registrar/editar`, mantener `ADMIN` para `eliminar/reactivar` y `reporte avanzado Ingresos vs Egresos` si se quiere |
| Configuración (precios, mora, becas, categorías, tipos uniforme) | ❌ solo lectura | ✅ | `views/configuracion/configuracion_view.py` + `services/configuracion_service.py` |
| Usuarios | ❌ | ✅ | `views/usuarios` |
| Auditoría | ❌ | ✅ solo lectura | `views/auditoria/auditoria_view.py` + `services/auditoria_service.py` |
| Backups: ver lista / crear backup | ✅ ver | ✅ ver+crear | `services/backup_service.py` |
| Backups: Restaurar / Rotar >30d / ver PIN | ❌ | ✅ | `services/backup_service.py:restaurar_backup(PIN)` gate |
| OneDrive / Ruta backup | ❌ | ✅ | `config.ini` |
| Tipos uniforme: crear/editar/desactivar | ❌ | ✅ | `services/tipo_uniforme_service.py` |
- **Flujo:** `main.py:Sidebar` ya filtra por `PERMISOS_ROL`; ajustar para que `Respaldo` siga visible a secretaria pero con boton `Restaurar` disabled + tooltip `Solo ADMIN`.

---

## 2) Alcance completo v2.1 (mapeo a DAYANNA_REVISION.md + Plan 5 Fases)

| # | Origen | Tarea | RN | Archivos principales | Verificación |
|---|---|---|---|---|---|
| 1.1 | Fase1 | Restringir `usuario.rol` a `ADMIN/SECRETARIA` (CHECK) + migración de `CAJA/INVENTARIO` existentes → `SECRETARIA` | RN-002 | `database/create_db.py:26`, `_migrar_columnas_faltantes()`, `database/seed.py` | `SELECT DISTINCT rol FROM usuario` solo 2 valores; login secretaria no ve `Configuración/Sistema→Usuarios/Auditoría` |
| 1.5 | Fase1 | Backup UTC-5 + doc Restore | — | `services/backup_service.py:listar_backups()`, `utils/dates.py`, `views/configuracion/configuracion_view.py:5.Respaldo` tooltip | `HH:MM (UTC-5)` en lista, dialog Restore explica overwrite+reinicio |
| A1 | Fase1 | Auditoría campo `usuario` (ya existe `log.id_usuario`, asegurar `nombre_usuario` en vista) | RN-032/050 | `repositories/log_repository.py`, `services/auditoria_service.py`, `views/auditoria/auditoria_view.py` | `SELECT tabla_afectada,accion,valor_nuevo FROM log` muestra usuario |
| A2 | Fase1 | Actualizador versiones (migraciones auto) | — | `main.py:40` + `database/create_db.py:create_tables()` `PRAGMA table_info` | `py main.py` sobre BD vieja migra sin error |
| 1.2 | Fase2 | Conceptos flexibles (catálogo `concepto_cobro`+`concepto_item`) | RN-052 | `database/create_db.py` nuevas tablas, `services/configuracion_service.py` CRUD, `views/configuracion`, `services/matricula_service.py:48` precedencia | Crear `Matrícula Promocional 150 incluye Camiseta` → matricular descuenta stock 1 y monto 150 |
| 1.6 | Fase2 | Fix botón Guardar Categoría (modal 440×520 grab_set) | — | `views/categorias/categoria_view.py` (copiar layout `estudiante_view.py:758`) | Botón visible sin scroll |
| 1.7 | Fase2 | Tipos Uniforme solo nombre | — | `views/inventario/tipo_uniforme_view.py`, `services/tipo_uniforme_service.py` quitar `descripcion/precio` del form | Form solo `Nombre` |
| 2.7.1 | Fase3 | Reingresante incluido en Activos | — | `repositories/estudiante_repository.py`, `views/estudiantes/estudiante_view.py` filtro | `Todos/Activos` muestra `ACTIVO+REINGRESANTE` |
| 2.7.2 | Fase3 | Matrícula +1/-1, totales fijos, MessageBox desglose | — | `views/matriculas/matricula_view.py:99` cards `-1/+1`, contenedor fijo totales, `messagebox.askyesno` antes de `matricula_service.crear_matricula` | Botones visibles, totales no scrollean, confirmación muestra `Tarifa 100 + Productos 20 =120` |
| 2.7.3 | Fase3 | `es_nuevo` + Camiseta S/0 única vez + bloqueo extras + reporte regalos | RN-051 | `database/create_db.py:estudiante.es_nuevo`, `services/estudiante_service.py`, `services/matricula_service.py:57` lógica camiseta 0, `services/reporte_service.py` | Crear estudiante `es_nuevo=1` → matricular genera `venta INSCRIPCION 0` 1 camiseta, no deja añadir extras, 2º edit disabled, reporte cuenta regalos |
| 2.7.4 | Fase4 | Pagos: estado visible + buscador DNI/Nombre + Limpiar | — | `views/pagos/pago_view.py`, `services/pago_service.py` mover validación `YAPE requiere comprobante` a Service, `repositories/pago_repository.py` buscador | Buscar `70645229` filtra, `YAPE` sin file bloquea desde backend `py -c` |
| 2.7.5 | Fase4 | Egresos secretaria crear/editar | — | `controllers/egreso_controller.py`, `services/egreso_service.py:14`, `views/egresos/egreso_view.py:161` mover SQL a Repo | Secretaria registra `PROFESOR 200`, Admin borra |
| 2.7.6-7 | Fase4 | Finanzas detalle + Becas/Conceptos | RN-011/052 | `services/beca_service.py`, `views/becas`, tablas `concepto_cobro` | CRUD beca `25%` asigna a matrícula recalcula `PAGADO` |
| 2.7.6 | Fase5 | Dashboard card Nuevos | — | `services/dashboard_service.py`, `views/dashboard/dashboard_view.py:148` 15ª card | `Nuevos (es_nuevo=1)` mes actual |
| 2.7.7 | Fase5 | Reportes Exportar Excel fix | — | `views/reportes/reporte_view.py:188` mover SQL a Service, modal responsive | Botón siempre visible |
| G | Fase5 | UI estándar + SQL en View fix | AGENTS | `views/egresos`, `views/reportes`, `utils/ui_helpers.py:crear_boton_interactivo` | `grep -r "cursor.execute" views/` solo 0 hits |

---

## 3) Cambios de BD (DDL + migración)

```sql
-- estudiante: flag nuevo (única vez)
ALTER TABLE estudiante ADD COLUMN es_nuevo INTEGER DEFAULT 0 CHECK(es_nuevo IN (0,1));
CREATE INDEX IF NOT EXISTS idx_estudiante_es_nuevo ON estudiante(es_nuevo);

-- concepto flexible (evita redundancia con configuracion.precio_* y tarifa)
CREATE TABLE IF NOT EXISTS concepto_cobro (
  id_concepto INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre TEXT UNIQUE NOT NULL,
  tipo TEXT NOT NULL CHECK(tipo IN ('INSCRIPCION','MENSUALIDAD','REINGRESO','PROMOCION','CAMPEONATO','OTRO')),
  monto REAL NOT NULL CHECK(monto >= 0),
  descripcion TEXT,
  activo INTEGER DEFAULT 1
);
CREATE TABLE IF NOT EXISTS concepto_item (
  id_item INTEGER PRIMARY KEY AUTOINCREMENT,
  id_concepto INTEGER NOT NULL REFERENCES concepto_cobro(id_concepto),
  id_producto INTEGER NOT NULL REFERENCES producto(id_producto),
  cantidad INTEGER NOT NULL DEFAULT 1 CHECK(cantidad > 0),
  UNIQUE(id_concepto, id_producto)
);
CREATE INDEX IF NOT EXISTS idx_concepto_tipo ON concepto_cobro(tipo);
CREATE INDEX IF NOT EXISTS idx_concepto_item_concepto ON concepto_item(id_concepto);

-- usuario: restringir a 2 roles (migración mapea CAJA/INVENTARIO → SECRETARIA)
-- Se hará en _migrar_columnas_faltantes(): ALTER RENAME + CREATE CHECK('ADMIN','SECRETARIA') + COPY + DROP

-- log ya tiene id_usuario; solo asegurar índice
CREATE INDEX IF NOT EXISTS idx_log_usuario ON log(id_usuario);
CREATE INDEX IF NOT EXISTS idx_log_fecha ON log(fecha);
```

Migración idempotente en `database/create_db.py:_migrar_columnas_faltantes()` con `PRAGMA table_info()` como ya hace para `estudiante.foto_path:399`.

---

## 4) Reglas de negocio nuevas (resumen para RN)

- **RN-051 Estudiante Nuevo + Camiseta costo 0 (única vez)**
  Tabla `estudiante.es_nuevo`. Al crear con `es_nuevo=1`, la primera `crear_matricula()` genera automáticamente `venta tipo=INSCRIPCION monto_total=0 detalle 1× Camiseta Entrenamiento` + `movimiento_inventario SALIDA 1 motivo='Regalo inscripción nuevo'` + `stock-1` atomico. Validación `stock<1 → ValueError Stock insuficiente` bloquea matrícula (rollback). Si `es_nuevo=0` (cargas existentes) no genera regalo. Después de la primera matrícula, `es_nuevo` queda inmutable. Mientras `es_nuevo=1` y no se haya usado el regalo, el UI de matrícula bloquea añadir productos extra (RN-051 "sin adicionales") para evitar confusión; si quiere comprar aparte, que use `Ventas`.

- **RN-052 Conceptos flexibles sin redundancia**
  `concepto_cobro`+`concepto_item` como catálogo único de bundles. `configuracion.precio_*` quedan como fallback. Precedencia de monto definida arriba. `auditoria_service` loguea `INSERT concepto_cobro` y cada `venta` generada por concepto. `tipo_uniforme` y `producto` siguen siendo la fuente de productos.

- **RN-002 actualizado (roles)**
  Solo `ADMIN` y `SECRETARIA`. Migración mapea `CAJA→SECRETARIA`, `INVENTARIO→SECRETARIA` conservando `activo` y `password_hash`.

- **RN-034/035 auditoría** sin cambio, solo se documenta que `log` ya incluye `id_usuario` y se mostrará `nombre_usuario` vía JOIN `persona`.

---

## 5) Orden de ejecución recomendado (sin bloqueos)

1. **Rápidos sin BD:** 1.6, 1.7, 2.7.1, G fix SQL views, 2.7.7, 1.5 tooltip UTC-5
2. **BD + migración:** 1.1 roles, 3 estudiante.es_nuevo, 3 concepto_cobro (1 migración atomica)
3. **Services:** RN-051 camiseta 0 en `matricula_service.py:57`, RN-052 concepto en `matricula_service.py:98`, mover validación comprobante a `pago_service.py:42`
4. **Vistas:** checkbox `es_nuevo` + badge + bloqueo extras, `-1/+1` + totales fijos + MessageBox, combo `Concepto` + multiselector productos, buscador pagos, permisos egresos/backup secretaria, dashboard 15ª card
5. **Reportes:** regalos mensual + ingresos vs egresos ya existen, añadir `concepto_cobro` en reporte si hace falta
6. **Verificación:** `pytest tests/test_matriculas_reingreso.py` + `py -c` backend probes + checklist `DAYANNA_REVISION.md:184` + export Excel en ruta `OneDrive\BackupsAcademia`

---

## 6) Criterios de aceptación v2.1

- [ ] `SELECT sql FROM sqlite_master WHERE name='usuario'` contiene `CHECK(rol IN ('ADMIN','SECRETARIA'))` y no hay filas con otros roles
- [ ] Secretaria puede `Registrar Egreso` y `Ver Pagos por DNI`, pero `Restaurar Backup` muestra `Solo ADMIN` y `Auditoría` `Acceso denegado`
- [ ] Crear estudiante `DNI 99999999 es_nuevo=1` → editar lo muestra disabled; no se puede cambiar a `0`
- [ ] Matricular ese nuevo en `concepto_item` vacío con `es_nuevo=1` → `producto Camiseta stock 50→49`, `venta INSCRIPCION 0`, `movimiento SALIDA`, `log` y UI no permitió añadir extra
- [ ] Crear concepto `Promoción 150 incluye Camiseta+Media` → matricular otro alumno con ese concepto → `venta` 2 detalles, `stock` -1 cada uno, `importe total 150` (no 100+20)
- [ ] Matrícula sin concepto usa `configuracion.precio_inscripcion` (fallback) y `tarifa.monto` si hay `monto_pactado` null
- [ ] Backup lista muestra `2026-09-06 18:53 (UTC-5)` y dialog Restore explica overwrite+reinicio
- [ ] `grep` no halla `cursor.execute` en `views/` y `pylint` capa ok

---

## 7) Riesgos y mitigaciones

- **Cargas existentes:** Al añadir `es_nuevo DEFAULT 0` todas las filas históricas quedan `0` (correcto). No se necesita backfill.
- **Stock 0 camiseta:** `matricula_service.py:74` ya hace `raise ValueError` con rollback; con `es_nuevo=1` se mantiene.
- **Conflicto tarifa vs concepto:** Mitigado con precedencia 1>2 documentada; validación en Service lanza si ambos intentan setear `monto_pactado` y `id_concepto` a la vez.
- **Permisos secretaria:** No se da `DELETE` en egresos para no perder `activo=0` histórico; Admin puede rotar backups.

---

*Siguiente paso al aprobar este doc:* implementar BD + `estudiante.es_nuevo` + `concepto_cobro` y luego UI por fase, manteniendo `DAYANNA_REVISION.md` como checklist manual.
