# Revisión del Sistema — Academia Deportiva
### Para: Dayanna y asistente  •  v2.1 OneDrive + Flexible + Plan 2026-09-06 documentado
> **v2.1 documentado:** `docs/desarrollo/plan_dayanna_v2.1.md` resuelve 3 dudas: `es_nuevo` en `Estudiantes→Nuevo`, `concepto_cobro` sin redundancia con `configuracion.precio_*`, secretaria con egresos. RN-051/RN-052 + `estudiante.es_nuevo` + `concepto_cobro` en `sistema/`.
### Objetivo: Probar el sistema **como secretaria y admin reales**, anotando qué funciona, qué confunde y qué falta. Cada fila es una mini-prueba.

> **Cómo usar (a mano):** Abre `py main.py` → `admin / admin123` (primera vez pide cambio, ventana queda **al frente y centrada**). Sigue **Pasos para probar** y compara con **Debería pasar**. Marca `✅ Sí / ❌ No / ⚠️ A medias` y escribe en **¿Falta?** si algo no tiene sentido.
>
> **Con opencode (asistente):** Dile “probar matrícula con producto uniforme” y él leerá `services/matricula_service.py` y ejecutará `py -c` sin abrir ventana. Usa `docs/README.md` como índice y `AGENTS.md` como reglas.
>
> **2 READMEs, ¿es normal?** Sí. `README.md` (raíz) es la portada que ve GitHub. `docs/README.md` es el índice de `docs/` (`sistema/`, `desarrollo/`, `despliegue/`, `manuales/`, `testing/`). Se mantienen los dos. Ya reorganizamos `docs/` en carpetas y `AGENTS.md` apunta a la nueva ruta.

---

## Novedades desde tu última revisión (qué probar primero)

| Tema | Qué cambió | Dónde verlo |
|---|---|---|
| **Menú agrupado** | De 13 botones planos a **5 grupos** `PANEL / ACADEMIA / FINANZAS / ALMACÉN / ANÁLISIS / SISTEMA` con scroll si no cabe. **No se corta** en `Reportes` | Sidebar morado, headers `11 bold #9CA3AF` |
| **Letra y hover** | Letra más grande (default `1.05x`), botones cambian a `hand2` + borde `#7C3AED` al pasar mouse; se nota qué es clickeable vs texto fijo | Pasa el mouse por cualquier botón/card |
| **Fechas** | `DatePicker` nuevo: puedes **escribir** `2026-09-15` o **clickear** `Día/Mes/Año` + `Hoy`. Sincroniza ambos | `Estudiantes → Fecha nacimiento`, `Pagos → Fecha Inicio/Fin` |
| **Mensajes** | Todo con `⏳ Guardando...` → `✅ Se guardó` / `❌ error` con color, auto-cierre 0.4s | `Configuración → Guardar`, `Estudiantes → Guardar` |
| **Ventanas** | Cada `Toplevel` (Nuevo alumno, Asociar apoderado, Venta reingreso) tiene `Cancelar/Guardar` + `X` y `grab_set` (no se pierde detrás) | Abre cualquier `+ Nuevo` |
| **Configuración ordenada** | 8 secciones numeradas `1. General … 8. Visual` sin texto sobrepuesto al mover mouse (fix wraplength) | `Sistema → Configuración` |
| **Matrícula + productos** | En `Registrar Matrícula` ahora ves **productos configurables** (uniformes) como cards `+ Añadir` que suman al `Importe total` y descuentan stock al guardar | `Matrículas → Registrar` abajo |
| **Foto/comprobante** | Foto `90×90` grande + preview en form, comprobante `70` thumb + click amplía | `Estudiantes` card y `Pagos` card |

---

## 0) Antes de empezar — Preparación (2 min)

| Paso | Debería pasar | ¿Viste? |
|---|---|---|
| 1. Doble clic `setup_onedrive.bat` (o `py main.py` si es local) | Crea `OneDrive\Academia\academia.db` y `fotos/`, `comprobantes/`, `BackupsAcademia` + `config.ini` |  |
| 2. Abrir app → `admin / admin123` | **Ventana cambio** `440×460` queda **al frente y centrada** sobre Dashboard (no se va al costado). Fondo no queda blanco (ves Dashboard detrás). |  |
| 3. Cambiar a clave nueva (6+ caracteres) | `✅ Contraseña cambiada` y entra al Dashboard. Si dejas vacío, no deja. |  |

**Anota si:** ventana se esconde / queda blanco / no avisa. **Tip:** `OneDrive` debe estar verde antes.

---

## 1) Configuración (solo ADMIN) — Todo sin código, ordenado y explicado

**Dónde:** `Sistema → Configuración` (ahora **8 secciones** con número, icono y ayuda `↳` gris, sin texto sobrepuesto al mover mouse).

| # | Probar (paso a paso) | Debería pasar (qué ves) | ¿Funciona? `✅/❌/⚠️` | ¿Falta / sin sentido? | Notas (foto, mensaje) |
|---|---|---|---|---|---|
| 1 | `1. 🏫 General` → cambia `Nombre` `Roncalli` → `Guardar` | Arriba `✅ Se guardó` verde, luego `Exportar Excel` sale con `Roncalli` | | | |
| 2 | `2. 💰 Precios` → `Inscripción 100 → 120` → `Guardar` → `Academia → Estudiantes → Nuevo` + `Matrículas → + Nueva` | Nueva matrícula **usa 120**, la vieja sigue 100. Debajo de cada campo ves `↳ Incluye 1 camiseta (-1 stock)` | | | |
| 3 | `3. ⏰ Mora` activa `Habilitar mora` + `5%` → `Guardar` | `Dashboard → Monto vencido` sube 5% al vencer. Si deshabilitas, solo cambia a `VENCIDO` sin recargo. | | | |
| 4 | `4. 📅 Cuotas y Becas` → desactiva `Permitir múltiples` → intenta matrícula con 2 becas | Mensaje `❌ No permite múltiples` rojo, no deja guardar | | | |
| 5 | `5. 💾 Respaldo` → mira `Ruta OneDrive\BackupsAcademia` + lista `2026-09-05 22:00 12MB a3f4` con `Verificar`/`Restaurar`/`Rotar >30d` | `Respaldo` en sidebar (solo muestra mensaje, **no queda activo** como vista) sigue en `Pagos` | | | |
| 6 | `6. 👥 Categorías` → `+ Nueva` `3-5` `3` `5` → `Guardar` → `Editar` → `Desactivar` | Card `🏷 3-5 | Edad 3-5` con `✏ Editar` `⛔ Desactivar` (hover `#F3E8FF` + mano) | | | |
| 7 | `7. 👕 Tipos Uniforme` → `+ Nuevo` `Uniforme Prueba` → aparece en `Almacén → Inventario → Tipo uniforme` → `Desactivar` desaparece | Lista sin `hover` que hacía “se corre” (fix) | | | |
| 8 | `8. 🎨 Apariencia` → `Tamaño Grande` → `Aplicar vista previa` (se agranda al instante) → `Guardar` → Reinicia y queda grande | `1.05 default` ya es más grande que antes; `Pequeña 0.95 / Grande 1.15 / Extra 1.32` | | | |
| 9 | Pasa el mouse por cualquier `entry` o botón | `Borde #7C3AED` y `cursor mano` → sabes qué es clickeable vs texto fijo | | | |

> **Tip:** Letra ahora `Menú 14 bold` + `Config 14` + `entries 12`. Si aún la ves chica, usa `Apariencia → Grande`.

---

## 2) Estudiantes + Foto grande + Apoderados (SECRETARIA y ADMIN)

**Tipografía y hover:** títulos `18 bold`, `card` con `hover #F3E8FF` + `mano`, mensajes `⏳ Guardando... → ✅` verde con auto-cierre.

| # | Probar | Debería pasar (qué ves) | ¿Funciona? | ¿Falta / sin sentido? | Notas |
|---|---|---|---|---|---|
| 1 | `Academia → Estudiantes → + Nuevo` → `Tipo Doc DNI/CARNET` `DNI 8 / CARNET 9`, `Fecha nacimiento` **escribe** `2020-03-15` **o** elige `Día/Mes/Año` + `Hoy` (sincroniza) | Si pones `7` dígitos dice `❌ DNI debe tener 8` rojo | | | |
| 2 | `Foto del niño (opcional) → 📷 Seleccionar foto` `jpg/png ≤2MB` | Label `✅ foto.jpg` + **preview 80×80** en form. Al guardar copia a `OneDrive\Academia\fotos\DNI.jpg`. En lista **miniatura 90×90** con borde `white`, `📷 nombre.jpg (clic para ampliar)` | | | |
| 3 | `Apoderado Principal` `DNI, nombres, parentesco` → `Guardar` | `✅ Estudiante y apoderado registrados` verde, aparece en `Activos`. Botones `Guardar` morado + `Cancelar` gris siempre visibles + `X` | | | |
| 4 | Buscar nombre/DNI + `Todos/Activos/Retirados/Reingresantes` | Filtra al instante, sin recargar | | | |
| 5 | `Editar` → cambiar foto → `Guardar` | Foto nueva reemplaza, `LOG` `foto_path` auditado | | | |
| 6 | `Retirar` → confirma | Pasa a `RETIRADO` `rojo`, cierra matrícula | | | |
| 7 | `Reingreso` → `¿Vender uniforme ahora?` → `Tipo Entrenamiento 20` `Cantidad 1` → `Vender` | `REINGRESANTE` naranja, dialog vende `stock-1` o `Omitir`. Luego `Matrículas` `precio_reingreso 100` sin camiseta auto | | | |
| 8 | `Apoderados` tab → `+ Asociar` → `DNI` → secundario `Madre` → `Quitar` secundario OK, principal `❌ No se puede desasociar principal` | Respeta `1 principal` único (antes dejaba sin principal) | | | |

---

## 3) Matrículas — Productos configurables a un clic

**Dónde:** `Academia → Matrículas → + Nueva` (ahora con **productos**).

| # | Probar | Debería pasar (qué ves) | ¿Funciona? | ¿Falta? |
|---|---|---|---|---|
| 1 | Elige `Estudiante` `ACTIVO/REINGRESANTE` → sugiere `Tarifa` por edad | `Tarifa` se autoselecciona; si ya tiene `ACTIVO` dice `ya tiene matrícula activa` | | |
| 2 | `Monto pactado` vacío = `tarifa`, `0` = gratuito | Cuota `0` `PAGADO` al instante | | |
| 3 | `Pago diferido` `2 meses` → `Registrar` | Crea **2 cuotas** `PENDIENTE` `2026-09, 2026-10`; `Ahora` 1 | | |
| 4 | `Beca 25%` → `Registrar` | Cuota `120 → 90`; `0 + 25% → 0`; `2 becas` con `permitir=0` bloquea `❌` | | |
| 5 | **Productos adicionales** abajo → ver cards `Uniforme Entrenamiento S/20 stock 10` con `+ Añadir` (hover morado + mano) → clic | Se marca `Seleccionados: Uniforme x1` azul + `Total matricula: S/100 | Productos: S/20 | Importe total: S/120` se actualiza solo | | |
| 6 | Con 1-2 productos seleccionados → `Registrar Matrícula` | `✅ Matrícula registrada` + en `Inventario` `stock 10→9` + `Ventas` aparece `UNIFORME 20` + `Auditoría` `venta UNIFORME`. Si `stock 0` dice `Stock insuficiente (disp: 1)` y **no crea matrícula** (rollback). | | | |
| 7 | **Primera matrícula** nuevo → `Stock Camiseta 50→49` auto (INSCRIPCION 0) | `Historial` `SALIDA Inscripción` | | |
| 8 | **Reingreso** 2ª matrícula | **No descuenta** camiseta; si quiere, añádelo en `Productos` arriba o luego en `Ventas` | | | |

---

## 4) Pagos y Cuotas (SECRETARIA) — Fechas escribir o clickear

| # | Probar | Debería pasar (qué ves) | ¿Funciona? | Notas |
|---|---|---|---|---|
| 1 | `Finanzas → Pagos → + Nuevo Pago` → `Estudiante` → `Cuota pendiente` `2026-09 - S/90 PENDIENTE` → `Monto 50` → `Método YAPE` → **sin comprobante** | Mensaje `Suba comprobante para YAPE...` naranja, no deja guardar. `📎 Seleccionar comprobante` + `preview 70` si es imagen | | |
| 2 | Subir `jpg/png ≤5MB` → label `✅ foto.jpg` + miniatura | `Registrar Pago` → `✅ Pago registrado. Saldo: 40.00` verde, cuota `PARCIAL`; pagar `40` → `PAGADO` y genera siguiente mes `monto_base` | | | |
| 3 | `Filtros Fecha Inicio/Fin` → **escribe** `2026-09-01` **o** elige `Día/Mes/Año` + `Hoy` (sincroniza) → `🔍 Buscar` | Filtra; `🧹 Limpiar` borra. Si `inicio>fin` rojo `La fecha de inicio debe ser anterior...` | | | |
| 4 | `Morosos` → `Actualizar` | Lista `Venció: 2026-08-10 Saldo: 90` rojo o `No hay cuotas vencidas` verde `Total: 0` | | | |
| 5 | `Historial → Buscar por recibo` `R2026...` | Filtra al vuelo, `✅ Total: 3 pago(s) • 150 S/` | | | |

---

## 5) Ventas (Uniformes/Tienda/Campeonato) — Nuevo

| Probar | Debería pasar |
|---|---|
| 1. `Finanzas → Ventas → Registrar Venta` → `Producto` (`CAMISETA-ENT S/20 stock:49`) → `Cantidad 2` → `Tipo UNIFORME` `Método EFECTIVO` → `Registrar` | `Venta R...` stock `49→47`, `Ganancia = venta-compra` visible en `Almacén → Productos`, `LOG venta`. Si `cantidad>stock` dice `Stock insuficiente`. |
| 2. `TIENDA` `Gaseosa` `precio_compra 8 venta 20` → vende 1 | `Stock-1`, `ganancia 12` en card `Almacén`. |
| 3. `INSCRIPCION` ya la hace matrícula auto (ver 3.4), no manual. |

---

## 6) Inventario / Almacén

| Probar | Debería pasar |
|---|---|
| 1. `Almacén → Inventario → Productos` card muestra `Código - Nombre`, `Categoría \| Tipo \| Compra S/8 Venta S/20 Ganancia 12 \| Uniforme: Entrenamiento`, `Stock: 47 \| Mín:5` rojo si `≤ mínimo` | Antes solo `Precio`, ahora `Compra/Venta/Ganancia + tipo_uniforme`. |
| 2. `Registrar Producto` → `Nombre, Categoría, Tipo uso (VENTA/CONSUMO_INTERNO), Stock mínimo, Precio, Compra, Venta, Tipo uniforme` → `Guardar` | Mensaje `✅ Se guardó`, sin `tipo_uniforme` guarda `Sin tipo`. |
| 3. `Movimiento` → `Producto, Tipo ENTRADA/SALIDA/AJUSTE, Cantidad, Motivo` → `Registrar` | Actualiza `stock` + `movimiento_inventario` nunca se borra. |
| 4. `Stock bajo` en `Dashboard` | Lista si `stock ≤ mínimo`. |

---

## 7) Egresos (solo ADMIN)

| Probar | Debería pasar |
|---|---|
| 1. `Finanzas → Egresos` (si no eres ADMIN no ves) → `Registrar Egreso` → `Concepto PROFESOR/PERSONAL/CAMPEONATO_FIJO/ARBITRAJE/VIATICOS`, `Monto 200`, `Fecha hoy` (escribir `2026-09-06` o combos), `Responsable` → `Guardar` | `✅ Egreso registrado`, `soft_delete` `activo=0` (no `DELETE`). Si `monto ≤0` o concepto inválido dice `Concepto no válido`. Si `SECRETARIA` intenta `Solo ADMIN...` |
| 2. `Reporte` tab → `Calcular` | `Ingresos ventas 60 + pagos 0 = 60, Egresos 350, Neto -290` (demo). |

---

## 8) Dashboard (14 cards) — Más lleno, tipografía grande

| Probar | Debería pasar |
|---|---|
| Abrir `Panel → Dashboard` | Header `📊 Dashboard • Resumen operativo` `26 bold`, 5 filas `110px` cards con `valor 26 bold` + línea color + `hover #F3E8FF` + `cursor mano`. Filas: `Alumnos/Vencidas/Por vencer` / `Pagos hoy/Ingresos hoy/Ingresos mes` / `Monto vencido/por vencer/Stock bajo` / `Ventas mes/Egresos mes/Neto mes` / `Nuevos/Antiguos/Matrículas mes`. Clic card → detalle tabla 20 filas + gráfico si `matplotlib`. Mensaje `Haga clic...` centrado si no hay detalle. |

> Antes `letra chica y plana`, ahora `13-14` título + `26` valor + `border`.

---

## 9) Reportes (9)

| Probar | Debería pasar |
|---|---|
| `Análisis → Reportes` 6 base + 3 v2: `Ingresos vs Egresos`, `Stock bajo uniformes`, `Nuevos vs Antiguos` → `Exportar Excel` → elige `2026-09-01` a `2026-09-30` → guardar | Genera `.xlsx` con `openpyxl` en ruta elegida (recomendado `OneDrive\BackupsAcademia`). Si no hay datos sale `0` pero no error. |

---

## 10) Auditoría (solo ADMIN, solo lectura)

| Probar | Debería pasar |
|---|---|
| `Sistema → Auditoría` → filtro `Tabla: venta/egreso/tipo_uniforme/movimiento_inventario` + `Desde/Hasta` (escribir o combos) → `Buscar` | Tabla `Fecha, Usuario, Tabla, Acción (INSERT/UPDATE/DESACTIVACION), Registro` + `LOG` de `foto_path` y `comprobante`. `SECRETARIA` ve `Acceso denegado`. |

---

## 11) Configuración — Vista ordenada y explicada (7 secciones)

| Probar | Debería pasar |
|---|---|
| `Sistema → Configuración` | Secciones numeradas `1. 🏫 General` … `8. 🎨 Apariencia Visual` en `cards` blancas sin hover glitch, cada campo con `label 200 + entry 260` + `↳ ayuda 10px gris` (`Ej: Roncalli…`, `Si 7 días...`). Sin texto sobrepuesto al mover mouse (fix `wraplength 600-650`). |
| `8. Apariencia Visual` → `Tamaño Grande` → `Aplicar vista previa` | Escala `1.15x` `ctk.set_widget_scaling`, mensaje. `Guardar` persiste en `config_visual.json`, aplica al reiniciar (default `1.05` para no tan chica). |
| `Guardar Cambios` | `✅ Configuración actualizada` incluye `precio_*` (antes perdía precios). |

> **Antes:** letra pequeña → ahora `Menú 14 bold` + `Configuración 14` títulos, `12` labels, `11` ayuda.

---

## 12) Menú y navegación

| Probar | Debería pasar |
|---|---|
| Sidebar `240px` con `PANEL/ACADEMIA/FINANZAS/ALMACÉN/ANÁLISIS/SISTEMA` headers `11 bold #9CA3AF` + botones `38px` `14/13` | Scrolleable `CTkScrollableFrame` con `scrollbar #4E1D70` — si no caben (pantalla chica) puedes scrollear, `SISTEMA` ya se ve (antes solo hasta `Reportes`). |
| `Respaldo` | **No resalta** como vista; solo muestra `messagebox` `Respaldo creado: ...\academia_....db` y queda en la vista anterior (`Pagos` no queda con `Respaldo` activo). `Tarifas` icono `🏷` sin correrse (sin `border` en hover). |
| `👤 Admin` header `Admin • En línea ✎` | **Click** en la tarjeta `Click para editar perfil` → abre `Usuarios` (intuitivo, antes no era clickeable). Hover `border #7C3AED` + `hand2`. |

---

## 13) Casos borde a anotar

- [ ] ¿1ª matrícula con `stock 0` camiseta bloquea? Debería decir `Stock insuficiente`.
- [ ] ¿Reingreso sin vender uniforme no descuenta? Debería quedar `stock` igual y luego venta manual sí descuenta.
- [ ] ¿Beca `25% + 20` con `permitir=0` bloquea segunda? ¿Y `desasignar` recalcula `PENDIENTE` `90→70→90`?
- [ ] ¿Foto `>2MB` rechaza? ¿Comprobante `YAPE` sin archivo avisa naranja?
- [ ] ¿`OneDrive\Academia\academia.db` se ve en ambas PCs tras `setup_onedrive.bat` + `py main.py`?

---

## Para el asistente (opencode)

```bash
# Ejecutar sin UI (backend)
py -c "import sys; sys.path.insert(0,'.'); from database.create_db import create_tables; create_tables(); from services import venta_service; venta_service.registrar_venta({'tipo_venta':'UNIFORME',...})"

# Probar apoderado principal único
# Debe fallar al desasociar principal, ok secundario
```

Usa `docs/README.md` como índice y `AGENTS.md` como fuente de verdad.

---
*Marca con `✅` `❌` `⚠️` y deja notas. Al final, lista 3 cosas que más confunden y 3 que faltan.*
