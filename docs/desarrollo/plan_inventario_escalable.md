# Plan de Desarrollo — Inventario Escalable (Academia Deportiva)

> **Fecha:** 2026-09-06 · **Versión:** 1.0 — Sistema actual v1.3 (`tipo_uniforme/venta/egreso` + OneDrive central) → **v2 escalable**. Intuitivo para secretaria (3 clics) y funcional para admin (sin código).
> **Relacionado:** `sistema/arquitectura_bd.md`, `sistema/diccionario_datos.md`, `sistema/reglas_negocio.md RN-024..027`, `sistema/casos_uso.md CU-010/011`, `sistema/arquitectura_software.md`, `docs/despliegue/despliegue_produccion.md`.

---

## 1. Objetivo

Pasar de **inventario único global** (`producto.stock_actual` `create_db:172`) a **inventario escalable** que soporte, sin reescribir: **tallas** (uniformes), **lotes y caducidad** (alimentos), **múltiples almacenes/cajas** (si abren 2 sedes), **proveedores y valorización**, manteniendo **3 clics** para vender y **stock siempre trazable** (`movimiento_inventario` nunca se borra `RN-024`).

---

## 2. Alcance: Actual vs Escalable

| Capacidad | Actual (suficiente 1 sede, 100 SKUs) | Escalable (2 sedes, 500 SKUs, tallas) |
|---|---|---|
| Stock | `producto.stock_actual` único global `repositories/producto_repository:69` | `stock_almacen(id_producto, id_almacen, stock)` + `stock_variante(id_producto, talla, stock)` |
| Variantes | `producto` duplicado por talla `CAMISETA-ENT-M` (confuso) | `producto_variante` `SKU` único `CAMISETA-ENT-M` con `talla` `S/M/L/XL` |
| Perecibles | Sin `fecha_caducidad` | `lote(codigo_lote, fecha_ingreso, fecha_caducidad, proveedor)` + alerta `vencidos` |
| Cajas | Sin `id_caja` en `venta:203` | `caja(id_caja, nombre, responsable, id_almacen)` + `venta.id_caja` + cierre `caja_sesion` |
| Valorización | Reporte `precio` pero no `stock*precio_venta` | Reporte `Valorizado` + `Ganancia = (venta - compra)*cantidad` |
| Performance | `SELECT *` sin paginación `producto_repository:47` | Paginación `LIMIT 50` + índice `producto(id_tipo_uniforme, activo)` |

**Mantener intuitivo:** secretaria no ve `id_almacen` si solo hay 1 (fallback `Almacén Principal`).

---

## 3. Requisitos

### 3.1 Funcionales

| ID | Requisito | Quién | Validación |
|---|---|---|---|
| **INV-01** | Crear producto con `categoría`, `tipo_uniforme` opcional, `talla` opcional `S/M/L/XL`, `stock_minimo`, `precio_compra/venta`, `id_almacen` (si 1, oculto) | ADMIN | `validate_not_empty(nombre)`, `tipo_uso VENTA/CONSUMO_INTERNO`, `stock_minimo>=0` |
| **INV-02** | Registrar movimiento `ENTRADA (+), SALIDA (- valida stock), AJUSTE (=)` con `motivo` + `usuario` | SECRETARIA | `cantidad>0`, `SALIDA` si `stock<cantidad` → `Stock insuficiente (disp X)` `venta_service:54` |
| **INV-03** | Vender `UNIFORME/TIENDA/CAMPEONATO/INSCRIPCION` por `caja` (si multi-caja) → descuenta `stock_almacen` + `movimiento SALIDA` + `detalle_venta` atómico `transaccion` `venta_service:44` | SECRETARIA | `stock_almacen < cant` bloquea, `comprobante_path` obligatorio si `≠EFECTIVO` `RN-042` |
| **INV-04** | Primera matrícula `-1 Camiseta Entrenamiento` solo si `es_primera && !reingreso` `matricula_service:59` (ya) | SISTEMA | Si `stock 0` → `ValueError` aborta matrícula |
| **INV-05** | Alertas `stock_bajo` (`stock <= minimo`), `por vencer` (`fecha_caducidad <= hoy+30`), `vencidos` | Dashboard | `producto_repository:59` + `lote.fecha_caducidad` |
| **INV-06** | Reportes Excel `openpyxl` `utils/excel_exporter:7` con `header #4472C4` + `TOTAL` + `AutoFilter` + `freeze` | ADMIN/SECRETARIA | `exportar_a_excel` + `TOTAL` fila negrita, `number_format S/ #,##0.00` |
| **INV-07** | Multi-almacén/caja opcional: si `COUNT(almacen)=1` UI no pide `almacén/caja` (retrocompatible) | ADMIN | `COUNT` decide si muestra `Combo Almacén/Caja` |

### 3.2 No funcionales

- **Intuitivo:** 3 clics: `Producto → Cantidad → Vender`. `DatePicker` escribir `YYYY-MM-DD` o combos `Día/Mes/Año` + `Hoy` `widgets/date_picker:31`.
- **Funcional offline OneDrive:** `WAL` `connection:29`, `config.ini` `OneDrive\Academia\academia.db` `constants:72`, `setup_onedrive.bat` crea `fotos/comprobantes`.
- **Escalable:** `LIMIT/OFFSET` + índices + `transaccion` evita TOCTOU `venta_service:46`.

---

## 4. Arquitectura Lógica (capas `AGENTS.md`)

### 4.1 DDL v2 escalable (`database/create_db.py:4` + `+ALTER IF NOT EXISTS`)

```sql
-- Catálogos
CREATE TABLE almacen (id_almacen PK, nombre UNIQUE, direccion, activo); -- seed: Principal
CREATE TABLE caja (id_caja PK, id_almacen FK, nombre UNIQUE, responsable, activo); -- seed: Caja 1
CREATE TABLE proveedor (id_proveedor PK, nombre UNIQUE, telefono, activo);
CREATE TABLE talla (id_talla PK, codigo UNIQUE); -- S,M,L,XL,UNICA
CREATE TABLE tipo_uniforme (id_tipo_uniforme PK, nombre UNIQUE); -- ya existe 196

-- Producto base (ya) + variante escalable
CREATE TABLE producto (id_producto PK, id_categoria_producto FK, tipo_uso CHECK, codigo UNIQUE, nombre, stock_actual (deprecated, usar stock_almacen), stock_minimo, precio, precio_compra, precio_venta, id_tipo_uniforme FK nullable, activo);
CREATE TABLE producto_variante (id_variante PK, id_producto FK, id_talla FK nullable, sku UNIQUE, codigo_barras, stock_minimo, activo);
CREATE TABLE stock_almacen (id_stock PK, id_producto FK, id_variante FK nullable, id_almacen FK, id_caja FK nullable, stock INTEGER DEFAULT 0, UNIQUE(id_producto, id_variante, id_almacen, id_caja));
CREATE TABLE lote (id_lote PK, id_producto FK, id_variante FK nullable, id_almacen FK, codigo_lote, fecha_ingreso TEXT, fecha_caducidad TEXT, id_proveedor FK, cantidad INTEGER, stock_restante INTEGER);

-- Movimiento trazable (extender, no romper)
CREATE TABLE movimiento_inventario (id_movimiento PK, id_producto FK, id_variante FK nullable, id_almacen FK, id_caja FK nullable, id_lote FK nullable, id_usuario FK, tipo_movimiento CHECK(ENTRADA,SALIDA,AJUSTE), cantidad, stock_anterior, stock_nuevo, fecha_movimiento, motivo);

-- Venta ya tiene tipo_venta, añadir caja
ALTER TABLE venta ADD id_almacen INTEGER REFERENCES almacen(id_almacen);
ALTER TABLE venta ADD id_caja INTEGER REFERENCES caja(id_caja);
ALTER TABLE detalle_venta ADD id_variante INTEGER REFERENCES producto_variante(id_variante);
ALTER TABLE detalle_venta ADD id_lote INTEGER REFERENCES lote(id_lote);

-- Índices
CREATE INDEX idx_stock_almacen_producto ON stock_almacen(id_producto);
CREATE INDEX idx_producto_variante_sku ON producto_variante(sku);
CREATE INDEX idx_lote_caducidad ON lote(fecha_caducidad);
CREATE INDEX idx_movimiento_almacen ON movimiento_inventario(id_almacen, id_producto);
```

**Migración:** `create_db.py:302` `_migrar_columnas_faltantes` `ALTER ADD COLUMN IF NOT EXISTS` para todo; `seed` `Almacén Principal + Caja 1 + Talla UNICA`.

### 4.2 Repositories (solo INSERT/SELECT/UPDATE)

- `producto_repository` → `obtener_por_sku`, `obtener_bajo_stock_por_almacen(almacen)`
- `stock_almacen_repository` → `obtener(id_producto, id_variante, id_almacen)`, `actualizar_stock(delta)`
- `lote_repository` → `obtener_vigentes() WHERE fecha_caducidad >= today`
- `movimiento_inventario_repository` → incluir `id_almacen, id_caja, id_variante, id_lote`

### 4.3 Services (toda regla `RN-024/027`)

- `inventario_service.registrar_movimiento` → exige `id_almacen` (default 1) + si `AJUSTE` es absoluto, si no delta + valida `lote` si perecible.
- `venta_service.registrar_venta` → dentro `transaccion` valida `stock_almacen >= cant` (no `producto.stock_actual`), descuenta `stock_almacen` + lote `stock_restante` FIFO, inserta `movimiento` con `id_almacen/id_caja/id_lote`.
- `producto_service` (o `inventario_service`) → `crear_producto` genera `sku = codigo-talla` si talla, crea `stock_almacen` 0 por almacén.

### 4.4 Controllers

- `inventario_controller.registrar_movimiento` → si `COUNT(almacen)=1` no pide `id_almacen` (usa 1).
- `venta_controller.registrar_venta` → si `COUNT(caja)=1` no pide `id_caja`.

---

## 5. Vistas — Intuitivas y Funcionales (3 clics)

### 5.1 Principio UI

- **Denso pero ordenado:** header `white 22 bold #1F0A33` + `card 110px` `border #E5E7EB` + `hover #F3E8FF` `ui_helpers:crear_card_interactiva`, tipografía `13 bold` título + `26` valor `dashboard_view:119`.
- **Distinguir interactivo vs estático:** botón `hover #4E1D70` + `cursor hand2` `main.py:205`, card `hover border #7C3AED`, `CTkEntry` `border #7C3AED` on focus `configuracion_view:125`.
- **Mensajes amigables:** `⏳ Guardando...` `#7C3AED` → `✅ Se guardó` verde / `❌` rojo `configuracion_view:272`, auto-cierre `400ms` + `500ms` recarga.

### 5.2 Inventario `views/inventario/inventario_view.py`

**Tabs (5, scrolleables):**

1. **Productos** (lista densa, no vacía)
   - Header `white` `Inventario de Productos` `22 bold` + `+ Nuevo` `130x36 #7C3AED` + filtros `white` `Buscar` `🔍` + `Stock bajo` rojo
   - Card `codigo - nombre` `14 bold` + `Compra S/8 Venta S/20 Ganancia 12 | Uniforme: Entrenamiento | Talla: M | Almacén: Principal` `12 gray` + `Stock: 47 | Mín:5` rojo si bajo + `Editar | Movimiento` `windos 70/90`
   - Si `COUNT(almacen)>1` selector `Almacén` arriba; si no, oculto.

2. **Categorías / Tipos uniforme** (ya `configuracion_view:107` pero también aquí)
   - `+ Nueva Categoría` + lista `🏷 3-5 | Edad 3-5` con `Editar/Desactivar` `card hover`.

3. **Registrar Producto** (form scrolleable, no vacío)
   - `Nombre*`, `Categoría*` combo, `Tipo uso` `VENTA/CONSUMO`, `Talla` `S/M/L/XL/UNICA` (si `VENTA` y `tipo_uniforme` → talla visible), `Stock mínimo`, `Precio`, `Compra`, `Venta` (se ve `Ganancia`), `Tipo uniforme` `Sin tipo`, `Almacén` (si >1), `Proveedor` (si alimento).
   - `Guardar` `120` `Actualizar` si edita + `Cancelar` gris + `label_form_status` `✅/❌`.

4. **Movimiento** (no vacía: preview stock)
   - `Producto` combo `400` + `Stock actual: 47` `12 bold #7C3AED` + `Tipo ENTRADA/SALIDA/AJUSTE` + `Cantidad` + `Almacén/Caja/Lote` (si multi) + `Motivo` + `Registrar Movimiento` `180`.

5. **Historial** (siempre con contenido o guía)
   - Si vacío `📭 No hay movimientos` + `Registra tu primer ENTRADA` (no solo `No hay...` gris). Si hay, cards `código - nombre` + `ENTRADA: 10 | Stock: 0→10` color `green/red/orange`.

### 5.3 Ventas `views/ventas/venta_view.py` (3 clics)

- **Registrar Venta** `UNIFORME/TIENDA/CAMPEONATO/INSCRIPCION` → `Producto` (filtra por `almacén` si >1) + `Variante/Talla` si tiene + `Cantidad` + `Tipo` + `Método` + `Almacén/Caja` (oculto si 1) + `Comprobante` `📎` + preview `70` thumb + `Registrar` → `Recibo R...` stock `47→46` + `LOG venta`.
- Si `producto` tiene `talla`, el combo muestra `CAMISETA-ENT-M (M, stock:10)` no solo `CAMISETA-ENT`.

### 5.4 Configuración `views/configuracion/configuracion_view.py:32` (8 secciones numeradas)

- `1. General` / `2. Precios Flexibles` (7 campos `↳ ayuda`) / `3. Mora` / `4. Cuotas y Becas` / `5. Backup OneDrive` / `6. Categorías` / `7. Tipos Uniforme` / `8. Apariencia Visual` `font_scale/tema` `config_visual.json` `1.05` default (letra no chica).
- Cada sección `card white` `header 14 bold #3D1559` + `ADMIN badge` + `nota ℹ` `11 #6B5B7B` `wraplength 650` sin hover glitch `border 0`.

---

## 6. Casos de uso clave (intuitivos)

| CU | Pasos (3 clics) | Si 1 almacén | Si 2 almacenes |
|---|---|---|---|
| **CU-011 Registrar Producto** | `Inventario → + Nuevo → Nombre + Categoría + Precios → Guardar → ✅` | `Almacén` oculto, `stock_almacen` Principal 0 | Elige `Almacén Principal/Secundaria` |
| **CU-010 Movimiento** | `Movimiento → Producto → Tipo ENTRADA 10 → Motivo → Registrar` | `stock_global 0→10` | `stock Principal 0→10` |
| **CU-019 Venta** | `Ventas → Producto M → Cant 2 → Vender → Recibo` | Descuenta global `50→48` | Elige `Caja 1` descuenta `Principal` |

---

## 7. Roadmap por sprints (sin romper v1.3)

| Sprint | Entregable | `file:line` | Criterio |
|---|---|---|---|
| **S1 (1d)** | `talla` + `producto_variante` + `precio_compra/venta` ya existe → UI talla + reporte valorizado | `inventario_view:154` + `reporte_service:162` `stock*precio_venta` | Crear `CAMISETA-ENT-M` stock 10, vender M descuenta M |
| **S2 (1d)** | `stock_almacen` + `almacen`/`caja` opcional (si `COUNT>1` muestra) | `create_db:166` `ALTER` | Con 1 almacén UI igual; con 2, `Almacén` visible |
| **S3 (0.5d)** | `lote` caducidad + alerta Dashboard `Por vencer 30d` | `lote.fecha_caducidad` + `dashboard_service:50` | Gaseosa vence `2026-10-01` → `por vencer` 30 |
| **S4 (0.5d)** | `proveedor` + paginación `LIMIT 50` + índices | `proveedor` + `producto_repository:47` | 500 SKUs sin lag |

**Migración:** todo `ALTER ADD COLUMN IF NOT EXISTS` `create_db:302` + `seed` `Almacén Principal`.

---

## 8. Criterios de aceptación

- [ ] `Inventario` nunca vacío: guía `📭` + `+ Nuevo` visible aunque 0.
- [ ] `talla` `S/M/L` crea `sku` único, vender `M` no toca `L`.
- [ ] `lote` `fecha_caducidad` alerta `por vencer` y bloquea `vencido`.
- [ ] Con 1 almacén, `Almacén/Caja` no aparece (retrocompatible).
- [ ] `Excel` `Inventario` con `SKU, Talla, Almacén, Stock, Precio Compra/Venta, Ganancia, Estado` + `TOTAL valorizado` negrita + `AutoFilter`.
- [ ] `transaccion` atomiza `venta` (stock + detalle + movimiento) sin `database is locked` OneDrive `WAL`.

---

> **Resultado:** Inventario escalable de 1 a N almacenes/cajas/tallas sin reescribir, manteniendo **3 clics** y **fachada simple si 1 almacén** (intuitivo), y **tablas nuevas solo si se necesitan** (funcional).
