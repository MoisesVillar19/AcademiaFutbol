# Manual del Sistema — Academia Deportiva (v2 Flexible + OneDrive)

> **Versión:** 1.0.0 · **Fecha:** 2026-09-06 · **BD Central:** `OneDrive\Academia\academia.db` · **Roles:** `ADMIN` / `SECRETARIA` · **Relacionado:** `cambios_RN_v2.md`, `despliegue_produccion.md`, `plan_deuda_tecnica.md`

---

## 1. Introducción

Sistema local con BD central en OneDrive (“web sin ser web”): cualquier PC instalada con el wizard apunta a la misma BD. Todos los precios, tipos de uniforme, descuentos y parámetros son **configurables sin código** por `ADMIN` en `Configuración`.

**Módulos:** `Dashboard`, `Estudiantes`, `Matrículas`, `Pagos`, `Ventas` (uniformes/tienda/campeonato), `Inventario`, `Egresos`, `Reportes`, `Auditoría`, `Configuración`, `Respaldo`.

---

## 2. Roles y permisos

| Acción | ADMIN | SECRETARIA |
|---|---|---|
| Dashboard / Reportes / Inventario (ver) / Estudiantes / Apoderados / Matrículas / Pagos / Ventas | ✅ | ✅ |
| Egresos (`PROFESOR/PERSONAL/CAMPEONATO`) + `Ingresos vs Egresos` | ✅ | ❌ |
| Usuarios / Tarifas / Categorías / Tipos uniforme / Precios / Mora / Backups / Auditoría / Importar | ✅ | ❌ |

*Sidebar `main.py:184` muestra `🛒 Ventas` a todos, `💸 Egresos` solo ADMIN.*

**Credenciales iniciales:** `admin / admin123` → obliga cambio `auth_service:73`. PIN emergencia hasheado `seed:64`.

---

## 3. Instalación funcional en PC (6 pasos — deja operativa)

**Requisito:** OneDrive instalado y sincronizado con la cuenta empresa (`admin@roncalli.onmicrosoft.com`).

1. **Ejecutar** `AcademiaFutbol-Setup-1.0.0.exe` → `Siguiente`
2. **Licencia** → Aceptar
3. **Carpeta** `C:\Program Files\AcademiaFutbol\` → `Siguiente`
4. **BD Central OneDrive** → `Ruta BD` autodetecta `C:\Users\{user}\OneDrive\Academia\academia.db` + `Ruta Backups` `OneDrive\BackupsAcademia` + `Fotos` `OneDrive\Academia\fotos` + `Comprobantes` `OneDrive\Academia\comprobantes` → **`Probar conexión` → ✔** → `Siguiente`
5. **Acceso directo** → marcar `Escritorio` → `Siguiente`
6. **Instalar** → escribe `C:\Program Files\AcademiaFutbol\config.ini` (`[database] path=...`) → `Finalizar → Abrir`

**Queda funcional:**
- `OneDrive\Academia\academia.db` creada con `create_tables:237` + `seed:73` (categorías `3-5..16-18`, tipos `Entrenamiento/Competencia/Completo/Media`, `CAMISETA-ENT` stock 50)
- `OneDrive\Academia\fotos\` y `comprobantes\` listos
- Primer arranque `admin/admin123` → cambiar contraseña

> Sin OneDrive: wizard avisa `Instalar OneDrive recomendado`, usa `APP_DIR\database\academia.db` local.

**Actualizar:** `main.py:344` auto-check GitHub cada 24h `updater/config.py:1` → diálogo `Nueva versión v1.1.0` → `Descargar` → `.exe` se actualiza, **BD no se toca** (`constants.py:9` `APP_DIR` vs `_internal`).

---

## 4. Configuración (ADMIN — todo flexible sin código)

`Configuración` (`configuracion_view.py:54` + `configuracion_service:22`) → `Guardar Cambios` → `LOG` `UPDATE`.

| Sección | Campos | Default | Qué hace |
|---|---|---|---|
| **General** | `Nombre academia, Dirección, Teléfono, Correo` | `Academia Deportiva` | Header reportes |
| **Precios flexibles** | `Inscripción (nuevo, incluye camiseta)`, `Mensualidad (antiguo)`, `Reingreso (con uniforme anterior)`, `Uniforme base`, `Tasa campeonato`, `Arbitraje por equipo`, `Pago profesor` | `100, 100, 100, 20, 15, 15, 200` | `RN-047` — usados en `matricula_service`/`venta_service`/`egreso_service` |
| **Mora** | `Habilitar Mora` `switch`, `Porcentaje (%)` | `0` | `RN-020` `cuota_service:150` `PORCENTAJE/MONTO_FIJO` |
| **Vencimiento** | `Días por vencer`, `Permitir múltiples becas` | `3, 1` | `RN-021/012` |
| **Backup** | `Automático`, `Frecuencia (días)`, `Ruta`, `Correo OneDrive` | `1, 7, backups/` | `RN-030` `main.py:242` cada 6h |
| **Categorías edad** | `3-5, 6-8, 9-12, 13-15, 16-18` CRUD | - | `categoria_service:31` |
| **Tipos uniforme** | `Entrenamiento, Competencia, Completo (30), Media (20)` CRUD | 4 seed | `tipo_uniforme_service:1` → `producto.id_tipo_uniforme` |

> Cambiar `Inscripción 100→120` se refleja en próxima matrícula sin deploy; cambiar `Uniforme base` no cambia `producto` con `precio_venta` ya creado (editar producto en `Inventario`).

---

## 5. Flujos principales (paso a paso)

### 5.1 Alumno nuevo + Inscripción (-1 uniforme) `RN-036`

1. `Estudiantes → Registrar / Editar` → `Tipo Doc. DNI/CARNET` `8/9 dígitos` → `Nombres, Apellidos, Fecha nac., Sexo, Dirección, Teléfono, Correo`
2. **Foto del niño (opcional):** `Seleccionar foto` `jpg/png ≤2MB` → `label` muestra nombre → copia a `OneDrive\Academia\fotos\{DNI}.jpg` `estudiante_view:383`/`FOTOS_DIR`
3. `Apoderado Principal` `DNI, Nombres, Apellidos, Parentesco (Padre/Madre...) Teléfono, Dirección` → `Guardar` → `estudiante_service:11` `transaccion` persona+estudiante `LOG`
4. `Matrículas → Registrar` → `Estudiante` (sugiere `Tarifa` por edad `matricula_controller:216`) → `Tarifa *` + `Monto pactado` opcional (deja vacío para `tarifa.monto` o `0` gratuito `is not None`) + `Día vencimiento 1-31` + `Beca` opcional + **`Pago diferido` `Ahora (0)`** → `Registrar Matrícula` → `cuota_service:71` genera **1 cuota** `PENDIENTE` `precio_inscripcion 100` + `venta INSCRIPCION` **-1 Camiseta Entrenamiento** `stock 50→49` `movimiento SALIDA` (si `stock<1` error)
5. `Pagos → Registrar Pago` → `Estudiante` → `Cuota pendiente` → `Monto` `100` → `Método` `YAPE` → **Subir comprobante** `jpg/png` → `COMPROBANTES_DIR` `OneDrive\Academia\comprobantes\{recibo}.jpg` `pago_view:110` → `Registrar` → `cuota PARCIAL/PAGADO` + siguiente cuota auto `cuota_service:118`

*Resultado:* `Dashboard → Nuevos Mes +1`, `Ingresos Mes +100`, `Inventario → Camiseta stock 49`, `Auditoría → venta INSCRIPCION`.

### 5.2 Mensualidad alumno antiguo + diferido 2-3 meses `RN-037/043`

1. `Matrículas` ya tiene `ACTIVO`; `Pagos` muestra `Cuotas vencidas/por vencer` `dashboard_service:17`
2. `Matrículas → Registrar` (si es re-matricula) → `Pago diferido` elige `2 meses` o `3 meses` → crea **2-3 cuotas** `PENDIENTE` correlativas `YYYY-MM` (`matricula_service:71` loop)
3. `Pagos → Registrar Pago` → `Monto` parcial `50` → `PARCIAL` saldo `50` → pagar resto `50` → `PAGADO` → genera siguiente mes automático
4. **Venta adicional opcional:** `Ventas → Producto` `Gaseosa` `TIENDA` `1×5` → no toca cuota, solo `stock-1` y `ingresos_ventas_mes`

### 5.3 Venta uniforme / tienda `RN-038/039/040`

1. `Ventas → Registrar Venta` → `Producto` (`codigo - nombre (S/venta stock)`) filtra por `tipo_uniforme` (`Entrenamiento 20 / Completo 30`) → `Cantidad` → `Tipo venta` `UNIFORME/TIENDA/CAMPEONATO/INSCRIPCION` → `Método` + `Comprobante` (obligatorio si `≠EFECTIVO`) + `ID Estudiante` opcional (para reingreso) → `Registrar Venta` → `venta_service:19` valida `stock>=cant`, calcula `precio_venta` o `monto_total` pactado (descuento flexible), `transaccion` `stock- cant` + `detalle_venta` + `movimiento SALIDA` + `LOG venta`
2. **Inventario:** `Inventario → Productos` card muestra `Compra S/8 Venta S/20 Ganancia 12 | Uniforme: Entrenamiento` `inventario_view:145`; `Registrar Producto` ahora pide `Compra/Venta/Tipo uniforme` `inventario_view:145`

### 5.4 Reingreso (sin uniforme, venta aparte) `RN-044`

1. `Estudiantes → Filtro Reingresantes → Retirados` → `Reingreso` botón naranja `estudiante_view:291` → `estudiante_service:140` `RETIRADO→REINGRESANTE` + cierra `matrícula ACTIVO→RETIRADO`
2. Dialog `¿Vender uniforme ahora?` → `Tipo uniforme` `Combo` + `Cantidad` → `Vender` → `venta UNIFORME` `1×20` stock `Competencia 30→29` visible en 2ª PC tras sync; `Omitir` deja reingreso sin uniforme
3. Luego `Matrículas → Registrar` con `precio_reingreso 100` (sin camiseta) — ahorro `20` vs nuevo `120`

### 5.5 Egresos `RN-046`

`Egresos` (ADMIN) → `Registrar Egreso` → `Concepto` `PROFESOR/PERSONAL/CAMPEONATO_FIJO/ARBITRAJE/VIATICOS` + `Monto` `>0` + `Fecha` + `Responsable` → `Guardar` → `egreso_service:10` `LOG`. `Reporte` tab `Ingresos vs Egresos` `2026-09-01→2026-09-30` → `Ingresos ventas+pagos 60 - Egresos 350 = Neto -290` (ejemplo).

---

## 6. Uso diario

**Secretaria:**
1. Abrir `AcademiaFutbol.exe` → `Dashboard` ver `Alumnos activos, Vencidas, Por vencer, Pagos hoy, Ingresos hoy/mes, Stock bajo, Ventas/Egresos/Neto, Nuevos/Antiguos`
2. `Estudiantes` buscar `DNI/nombre` + filtro `Activos/Retirados/Reingresantes` → `Editar/Retirar/Reingreso/Desactivar` (ADMIN)
3. `Apoderados` `+ Asociar` `DNI/CARNET` + `Parentesco` máx 2, 1 principal
4. `Pagos` `+ Nuevo Pago` + `Morosos` `Actualizar`
5. `Ventas` + `Inventario` `+ Nuevo` / `Movimiento ENTRADA/SALIDA`
6. `Reportes → Exportar Excel` elige `2026-09-01` a `2026-09-30` → guardar en `OneDrive\BackupsAcademia`

**ADMIN extra:**
- `Usuarios` crear `SECRETARIA` (1 usuario por persona `RN-002`), `Configuración` precios/tipos, `Auditoría` filtrar `usuario/matricula/venta...` + fecha, `Respaldo` `Crear manual` `configuracion_controller:40` → `OneDrive\BackupsAcademia\academia_YYYY-MM-DD_HH-MM-SS.db`, `Tarifas/Categorías/Importar` `CSV/XLSX`

**Fotos/Comprobantes:**
- Estudiante card muestra **thumbnail 60×60** si `foto_path` existe `PIL` + `click → os.startfile` amplía; sino texto `Foto: nombre.jpg`
- Pago/Venta card muestra `comprobante_path` texto + archivo en `OneDrive\Academia\comprobantes\{recibo}.jpg`

---

## 7. Reportes, Dashboard, Auditoría, Backup

| Módulo | Qué ver | Exportar |
|---|---|---|
| **Dashboard** 8+6 cards | `Alumnos, Vencidas, Por vencer, Pagos hoy, Ingresos hoy/mes, Monto vencido/por vencer, Stock bajo, Ventas mes, Egresos mes, Neto mes, Nuevos/Antiguos` | Click card → detalle tabla 20 filas + gráfico `matplotlib` si disponible |
| **Reportes** 9 | `Morosos, Pagos por fecha, Ingresos mensuales, Alumnos por categoría, Inventario, Becas activas, **Ingresos vs Egresos, Stock bajo uniformes, Nuevos vs Antiguos**` | Excel `reporte_{id}_{ini}_a_{fin}.xlsx` en ruta elegida |
| **Auditoría** | `Fecha, Usuario, Tabla (usuario/persona/estudiante/matricula/cuota/pago/producto/venta/egreso/tipo_uniforme), Acción INSERT/UPDATE/DESACTIVACION, Registro, Valor anterior/nuevo` | Solo lectura ADMIN `RN-035` |
| **Backup** | `BACKUP_DIR` `OneDrive\BackupsAcademia` + `main.py:242` cada 6h verifica `frecuencia_backup 7` | `Respaldo` botón manual + `restore.py` `close_connection + copy2` |

---

## 8. Configuración y flexibilidad

Todo sin código: `precio_inscripcion/mensualidad/reingreso/uniforme/tasa/arbitraje/pago_profesor`, `mora_habilitada/tipo/porcentaje`, `dias_por_vencer`, `permitir_multiples_becas`, `backup`, `categorías edad`, `tipos uniforme` + `beca PORCENTAJE/MONTO_FIJO` + `monto_pactado 0` gratuito. Cambia en `Configuración` y siguiente operación lo usa (`configuracion_service.obtener_valor`).

---

## 9. Solución de problemas

| Problema | Causa | Solución |
|---|---|---|
| `Database is locked` | 2 PCs `OneDrive` sin sync | Esperar icono verde OneDrive, `WAL` + `transaccion:43` reintenta recibo 3× |
| `academia (conflicto).db` | Edición offline simultánea | Cerrar PCs, OneDrive resuelve, restaurar último `backup` `restore.py` |
| Foto no se ve | `FOTOS_DIR` no existe o `PIL` no instalado | `pip install pillow`, `FOTOS_DIR` se crea `os.makedirs` |
| Config precios no guarda | No `ADMIN` | `Configuración` gate `ADMIN` `configuracion_controller:13` |
| Egreso no guarda | No `ADMIN` o `monto ≤0` | `egreso_service:20` valida `>0` `concepto` `PROFESOR...` |

---

## 10. Flujo OneDrive (BD no se mueve)

```
Wizard → config.ini [database] path=OneDrive\Academia\academia.db
APP 1 → OneDrive\Academia\academia.db (WAL) + fotos/ + comprobantes/
APP 2 → mismo path → sync verde → ventas/estudiantes visibles en ambas
Backup → OneDrive\BackupsAcademia\academia_*.db
```

*Sin OneDrive:* `APP_DIR\database\academia.db` + `APP_DIR\fotos` local (aviso wizard).

---

**Soporte:** `docs/despliegue_produccion.md:43` instalación 6 pasos deja funcional, `docs/cambios_RN_v2.md:1` RN flexibles, `docs/plan_deuda_tecnica.md:1` deuda `S1/S2/S3`.

