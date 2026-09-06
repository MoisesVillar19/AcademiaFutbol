# Cambios a Reglas de Negocio — v2.0 (Inscripción / Mensualidad / Uniformes / Ingresos y Egresos)

> **Fecha:** 2026-09-05 · **Versión base:** `reglas_negocio.md` RN-001..RN-035 · **Nuevas:** RN-036..RN-050 · **Origen:** Requerimientos empresa (sept 2026). Arranque desde 0 sin BD legado, **sistema 100% flexible y configurable** (ningún precio hardcodeado), **1ª matrícula descuenta -1 uniforme**, **reingreso = venta separada**. Centralizado OneDrive (ver `despliegue_produccion.md`).

### Principios de flexibilidad (consolidado)

1. **Todo parámetro en `CONFIGURACION`**: `precio_inscripcion, precio_mensualidad, precio_reingreso, precio_uniforme, tasa_campeonato, arbitraje, pago_profesor, dias_por_vencer, permitir_multiples_becas, ruta_backup, OneDrive` — lectura vía `configuracion_service.obtener_valor()` (`RN-029`), edición solo `ADMIN` `configuracion_controller:13`.
2. **Descuentos configurables**: `beca PORCENTAJE/MONTO_FIJO` (`RN-011`) + `monto_pactado` (`RN-010`, permite `0` gratuito) + `permitir_multiples_becas` (`RN-012`) aplicables a cualquier cobro; `venta` también admite descuento por `beca` o precio pactado sin código.
3. **Uniformes ampliables sin código**: `tipo_uniforme` CRUD `ADMIN`; cada tipo → `producto` con `id_tipo_uniforme`, `precio_compra/venta`, `stock`, `ganancia=venta-compra` calculada en Service.
4. **Reingreso flexible**: buscar `DNI` → reutiliza `persona/estudiante` existente, nueva `matricula` sin camiseta; uniforme se elige después como `venta` (tipo y precio configurables).

### Resumen de cambios

| Área | Antes (RN-001..035) | Nuevo (v2) | Impacto |
|---|---|---|---|
| Matrícula vs mensualidad | `RN-008/010` matrícula única con `monto_pactado` | **Separar** `Inscripción` (solo nuevos, incluye camiseta) y `Mensualidad` (solo antiguos, recurrente) — ambos configurables | `configuracion` + `producto` + `venta` |
| Inventario | `RN-025` 2 categorías genéricas, `RN-027` stock en `producto` | **Tipos uniforme específicos** + 3 tipos pago + tienda alimentos, todo parametrizado | `tipo_uniforme`, `precio_compra/venta/ganancia` |
| Uniformes | No existía | `Entrenamiento` obligatorio + `Competencia/Completo/Media` ampliables, precios configurables `20/30` | `categoria_producto` → `tipo_uniforme` |
| Descuentos | Fijo `beca` | **Configurable**: múltiples becas, monto pactado, descuento venta | `matricula_beca`, `configuracion` |
| Egresos | No existía | Pagos profesores/personal + campeonatos (tasas, arbitraje S/15, viáticos) parametrizados | `egreso` |
| Fotos/comprobantes | No | 1 foto niño + foto comprobante pago por alumno (OneDrive `fotos/`, `comprobantes/`) | `estudiante.foto_path`, `pago/venta.comprobante_path` |
| Pago diferido | No | Matrícula/mensualidad diferible 2-3 meses (genera N cuotas) | `cuota` múltiple |
| Precios | Fijos en tarifa | **100% configurables** por `configuracion` sin tocar código | `precio_inscripcion 100, mensualidad 100, reingreso 100, uniforme 20, paquete 20/30, profesor 200` |

---

### Nuevas reglas RN-036..RN-050

#### RN-036 Pago de Inscripción

Solo alumnos **nuevos** (`estudiante.estado=NUEVO` o primer ingreso).

| Campo | Valor |
|---|---|
| Precio | `configuracion.precio_inscripcion` configurable (ref `S/100.00`) |
| Incluye | 1 unidad `Camiseta Entrenamiento` (`producto` con `id_tipo_uniforme=Entrenamiento`) |
| Inventario | Descuenta **-1** `stock_actual` de `Camiseta Entrenamiento` + `movimiento_inventario tipo=SALIDA, motivo='Inscripción nuevo'` |
| Validación | Si `stock <1` → error `"Stock insuficiente de Camiseta Entrenamiento"`; operación atómica `transaccion` (`database/connection.py:43`) |
| Auditoría | `LOG tabla=venta/id_venta, accion=INSERT` + `movimiento_inventario` |

*Ejemplo:*

| Alumno | Fecha | Cobro | Stock antes | Stock después | Recibo |
|---|---|---|---|---|---|
| DNI 76543210 Nuevo | 2026-09-01 | S/100 YAPE foto `comprobantes/R20260901...jpg` | 50 | 49 | `R202609011234` |

#### RN-037 Mensualidad

Solo alumnos **antiguos** (`ACTIVO` o `REINGRESANTE` con matrícula vigente).

| Campo | Valor |
|---|---|
| Precio | `configuracion.precio_mensualidad` (ref `S/100/mes`) |
| Frecuencia | `RN-013` mensual única; no semanal/quincenal |
| Generación | `cuota_service.generar_siguiente_cuota` + `calendar.monthrange` (día 31→fin mes); si diferido 2-3 meses crea 2-3 cuotas `PENDIENTE` con `periodo YYYY-MM` correlativo |
| Inventario | **No** afecta |
| 3 tipos pago | `RN-023` `EFECTIVO/YAPE/PLIN/TRANSFERENCIA` — selector en `pago_view.py:101` |

*Ejemplo diferido:* Matrícula 2026-09-01 día venc 5 → si elige 3 meses → cuotas `2026-10-05 PENDIENTE 100`, `2026-11-05 100`, `2026-12-05 100`.

#### RN-038 Venta de Productos (Tienda)

Productos adicionales **no afectan mensualidad** (`RN-038`). Se venden vía `venta`+`detalle_venta` independiente de `cuota`.

| Producto | `precio_compra` | `precio_venta` | `ganancia=venta-compra` | Stock |
|---|---|---|---|---|
| Gaseosa 500ml | 2.50 | 5.00 | 2.50 | 100 |
| Pan con pollo | 3.00 | 6.00 | 3.00 | 40 |

Validación: `tipo_uso=VENTA`, `stock_actual >= cantidad`. Precio editable solo ADMIN.

#### RN-039 Tipos de Uniforme

Al menos 1: `Uniforme Entrenamiento` (`tipo_uniforme` tabla). Ampliables sin código (ADMIN `Configuración` → CRUD).

| id | nombre | variante | precio ref |
|---|---|---|---|
| 1 | Uniforme Entrenamiento | — | 20 |
| 2 | Uniforme Competencia | — | 20 |
| 3 | Uniforme Completo | incluye todo | 30 (paquete) |
| 4 | Uniforme Media | mitad | 20 |

Cada tipo → 1 `producto` con `id_tipo_uniforme` + `codigo` único (`PRD...` con `secrets`).

#### RN-040 Inventario Uniformes (flexible)

Toda **venta uniforme** y toda **1ª inscripción nuevo** descuenta stock del tipo vendido (`RN-040`). **A partir de la 2ª matrícula (reingreso u otro) ya cuenta como `venta` separada**: se busca al estudiante (`DNI`) y se elige uniforme (tipo y precio configurables); no hay descuento automático. Reingreso **no** descuenta por defecto (incluye uniforme anterior); si el reingresante pide nuevo uniforme se registra `venta tipo=UNIFORME` aparte (`S/20` configurable). Todo configurable: stock mínimo, `precio_uniforme` por tipo, `ganancia`.

Movimiento registrado en `movimiento_inventario:176` (`stock_anterior/nuevo`, `motivo='Inscripción nuevo'` vs `'Venta uniforme'`).

*Ejemplos:*

| Caso | Acción | Stock Camiseta | Venta |
|---|---|---|---|
| Nuevo DNI 76543210 | Inscripción 100 + -1 Camiseta Entrenamiento | 50→49 | Incluida en inscripción |
| Reingreso mismo DNI | Reingreso 100 (sin camiseta) | 49→49 | No |
| Reingreso + uniforme Competencia 25 | Venta aparte `Tipo Competencia 25` | 30→29 (Competencia) | `venta UNIFORME 25` |

Si `stock <1` al inscribir → error `Stock insuficiente` (no permite inscripción sin camiseta; ADMIN decide reponer o cambiar tipo).

#### RN-041 Foto del Alumno

1 imagen por estudiante (`estudiante.foto_path TEXT` → `APP_DIR/fotos/{dni}.jpg`). Subida en `estudiante_view.py`, validación `jpg/png ≤2MB`. Solo lectura si no es ADMIN/SECRETARIA creador.

#### RN-042 Comprobante de Pago (Foto)

Todo `pago` y `venta` guarda `comprobante_path` (`APP_DIR/comprobantes/{numero_recibo}.jpg`). Obligatorio si `metodo != EFECTIVO` (YAPE/PLIN). Vista `pago_view.py:184` card muestra miniatura + click amplía.

#### RN-043 Pago Diferido 2-3 Meses

Al matricular/inscribir, campo `diferir_meses: 0|2|3` persiste `matricula.fecha_inicio` y genera N cuotas pendientes futuras. `fecha_matricula` (texto `YYYY-MM-DD`) persiste aunque se pague después.

#### RN-044 Reingreso con Uniforme Anterior (flexible, configurable)

`RN-009` + `RN-044`: reingreso cuesta `precio_reingreso` (`100` configurable, menor que `nuevo 100 + uniforme 20 =120` porque reutiliza uniforme) → ahorro `20` configurable. Flujo: **buscar datos estudiante** por `DNI` (reutiliza `persona` existente) → `registrar_reingreso RETIRADO→REINGRESANTE` → nueva `matricula` sin camiseta; luego **buscar/seleccionar uniforme** entre tipos disponibles (`Entrenamiento 20, Competencia 25, Completo 30` etc.) y registrar `venta` aparte si lo requiere. Precios y tipos 100% parametrizados; descuento adicional vía `beca` o `monto_pactado` configurable.

Lógica en `matricula_service:77` `REINGRESANTE→ACTIVO` sin crear venta automática; `venta_service` valida stock y descuenta.

*Ejemplo flexible:* Reingreso con descuento beca 10% → `100 -10% =90` + `Uniforme Media 20` → total `110`; todo sin código, solo `configuracion` + `beca`.

#### RN-045 Ingresos Fijos

| Fuente | Tabla | Cálculo reporte |
|---|---|---|
| Matrícula/Inscripción nuevo | `matricula.monto_pactado=precio_inscripcion` + `pago` | `SUM monto_total WHERE periodo LIKE 'YYYY-MM%' AND es_inscripcion=1` |
| Reingreso | `matricula` con `estudiante previo RETIRADO` | idem |
| Mensualidad | `cuota/saldo` | `SUM detalle_pago` |
| Uniformes | `venta tipo=UNIFORME` | `SUM venta` |
| Tienda | `venta tipo=TIENDA` | `SUM (precio_venta)` + ganancia |
| Campeonatos | `venta tipo=CAMPEONATO` | `tasas + arbitraje 15×equipos + viáticos` |

*Paquetes:* `S/20 / S/30` configurables como `producto` bundle.

#### RN-046 Egresos Fijos

Nueva tabla `egreso` (`database/create_db.py:4`):

| Campo | Tipo | Ejemplo |
|---|---|---|
| `id_egreso` | PK | 1 |
| `concepto` | `CHECK('PROFESOR','PERSONAL','CAMPEONATO_FIJO','ARBITRAJE','VIATICOS')` | `PROFESOR` |
| `monto` | REAL | 200 |
| `fecha` | TEXT `YYYY-MM-DD` | 2026-09-05 |
| `responsable` | TEXT | Juan Pérez |
| `id_usuario` | FK | 1 |

Fijos: `2 profesores ×200 + 1 personal ×?` + por campeonato `fijos + profesores + insumos`. Reporte `Ingresos - Egresos = neto`.

#### RN-047 Precios Referenciales (100% configurables, RN-029)

| Parámetro | Default | Columna `configuracion` | Editable |
|---|---|---|---|
| `precio_inscripcion` | 100.00 | `REAL DEFAULT 100` | ADMIN `Configuración` |
| `precio_mensualidad` | 100.00 | `REAL DEFAULT 100` | ADMIN |
| `precio_reingreso` | 100.00 | `REAL DEFAULT 100` | ADMIN |
| `precio_uniforme` (base) | 20.00 | `REAL DEFAULT 20` | ADMIN; override por `producto.precio_venta` por tipo |
| `paquete_completo` | 30.00 | producto bundle `precio_venta=30` | ADMIN inventario |
| `paquete_media` | 20.00 | producto `precio_venta=20` | ADMIN |
| `tasa_campeonato` | 15.00 | `REAL DEFAULT 15` | ADMIN |
| `arbitraje_por_equipo` | 15.00 | `REAL DEFAULT 15` | ADMIN |
| `pago_profesor` | 200.00 | `egreso.monto` | ADMIN egresos |

Ningún precio hardcodeado en Services — leer vía `configuracion_service.obtener_valor()` o `producto.precio_venta` por tipo. Descuentos (`beca/monto_pactado`) también configurables y combinables según `permitir_multiples_becas`.

#### RN-048 3 Tipos de Pago

Mantener `RN-023` `EFECTIVO/YAPE/PLIN/TRANSFERENCIA` (3 tipos lógicos; `TRANSFERENCIA` engloba banco). Validación `validate_metodo_pago` en `pago_controller:18`.

#### RN-049 Reportes Ampliados

| Reporte | Campos | Fuente |
|---|---|---|
| Ingresos por mes | `mes, inscripciones, reingresos, mensualidades, tienda, uniformes, campeonatos, total` | `pago+venta+matricula` `excel_exporter.py:1` |
| Nuevos vs Antiguos | `mes, nuevos, antiguos, % nuevos` | `estudiante.fecha_ingreso` |
| Stock bajo uniformes | `producto, tipo_uniforme, stock, minimo` | `producto WHERE stock<=minimo` `dashboard_service:32` |
| Ingresos vs Egresos | `mes, ingresos, egresos fijos, campeonatos, neto` | `venta+egreso` |

#### RN-050 Auditoría Extendida

Todo `venta`, `egreso`, `tipo_uniforme`, `foto` registra `LOG` (`auditoria_service.registrar_insert/update`). Inmutable `RN-035`.

---

### Cambios en BD (delta v2)

```sql
-- configuracion: +4 precios
ALTER TABLE configuracion ADD precio_inscripcion REAL DEFAULT 100;
ADD precio_mensualidad REAL DEFAULT 100;
ADD precio_uniforme REAL DEFAULT 20;
ADD precio_reingreso REAL DEFAULT 100;

-- estudiante: fotos
ALTER TABLE estudiante ADD foto_path TEXT;
ADD comprobante_pago_path TEXT;
ADD fecha_matricula TEXT;

-- producto: costos tienda
ALTER TABLE producto ADD precio_compra REAL DEFAULT 0;
ADD precio_venta REAL DEFAULT 0;
ADD id_tipo_uniforme INTEGER REFERENCES tipo_uniforme(id_tipo_uniforme);

-- nuevas
CREATE TABLE tipo_uniforme (id_tipo_uniforme PK, nombre UNIQUE, descripcion, activo DEFAULT 1);
CREATE TABLE venta (id_venta PK, id_estudiante FK NULL, id_usuario FK, fecha_venta TEXT, monto_total REAL, metodo_pago CHECK, tipo_venta CHECK('UNIFORME','TIENDA','CAMPEONATO','INSCRIPCION'), numero_recibo UNIQUE, comprobante_path TEXT, activo DEFAULT 1);
CREATE TABLE detalle_venta (id_detalle PK, id_venta FK, id_producto FK, cantidad INTEGER, precio_unitario REAL, subtotal REAL);
CREATE TABLE egreso (id_egreso PK, concepto CHECK, monto REAL, fecha TEXT, responsable TEXT, id_usuario FK, observacion TEXT);
```

Índices nuevos: `idx_venta_fecha`, `idx_detalle_venta_venta`, `idx_egreso_fecha`.

### Flujos

**Flujo A — Nuevo alumno + inscripción**

```
1. UI Estudiantes → foto + DNI tipo_documento DNI/CARNET → estudiante_service.crear_estudiante (transaccion persona+estudiante)
2. cobrar_inscripcionService: with transaccion { venta UNIFORME Camiseta -1 stock + movimiento SALIDA; matricula monto=precio_inscripcion; cuota mes+1 mensualidad; pago foto comprobante }
3. Dashboard: ingresos+1, stock-1
```

**Flujo B — Mensualidad antiguo (diferido opcional)**

```
1. UI Pagos → cuotas pendientes (cuota_service)
2. pagar: monto 100 YAPE + comprobante; si diferir 3 → genera 3 cuotas PENDIENTE
3. Si vende Gaseosa → venta TIENDA separada, no toca cuota
```

**Flujo C — Venta uniforme/tienda**

```
1. UI Ventas → elige tipo_uniforme/producto → cantidad → venta_service.validar stock → transaccion stock- cant + movimiento + venta
```

**Reingreso:** `registrar_retiro → RETIRADO (matricula ACTIVO→RETIRADO)` → `registrar_reingreso → REINGRESANTE` → nueva `matricula precio_reingreso` sin camiseta.

### Criterios de aceptación v2

- [ ] Inscripción nuevo descuenta exactamente 1 Camiseta y falla si stock 0
- [ ] Mensualidad antiguo no descuenta inventario; configurable 100
- [ ] Venta uniforme descuenta stock tipo correcto; tienda calcula ganancia
- [ ] Foto niño y comprobante visibles y auditados
- [ ] Reingreso 100 sin uniforme; nuevo + uniforme 120; reportes separan nuevos/antiguos
- [ ] Reportes Excel: ingresos mes, stock bajo, ingresos vs egresos neto

### Trazabilidad RN→código (resumen)

| RN | Service | Repo/Modelo | Test esperado |
|---|---|---|---|
| 036-037 | `matricula_service`, `venta_service`, `pago_service` | `tipo_uniforme`, `producto` | `test_inscripcion_descuenta_stock` |
| 038-040 | `venta_service`, `inventario_service` | `movimiento_inventario` | `test_venta_uniforme_stock` |
| 041-042 | `estudiante_service`, `pago_service` | `estudiante.foto_path` | `test_foto_comprobante` |
| 045-046 | `reporte_service`, `dashboard_service` | `egreso`, `venta` | `test_reporte_ingresos_egresos` |
