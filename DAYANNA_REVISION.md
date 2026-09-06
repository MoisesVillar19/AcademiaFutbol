# Revisión del Sistema — Academia Deportiva
### Para: Dayanna y asistente
### Objetivo: Probar todo el sistema como lo haría una secretaria y un admin, anotando qué funciona, qué falta y qué no tiene sentido.

> **Cómo usar este documento:** Hay una tabla por módulo. Para cada fila haz:
> 1. Sigue el **Pasos para probar** tal cual.
> 2. Mira **Debería pasar** y compara con lo que ves.
> 3. Marca **¿Funciona?** `Sí` / `No` / `A medias`.
> 4. En **¿Falta o no tiene sentido?** escribe si algo sobra, confunde o falta (ej: “botón no dice qué hace”).
> 5. En **Notas** deja detalle (foto, mensaje que sale, etc.).
>
> Puedes revisarlo **a mano** abriendo la app (`py main.py` → `admin/admin123`) y también con **opencode**: pídele “probar el flujo de matrícula” y él ejecutará los pasos leyendo el código.
>
> **Sobre los 2 READMEs:** Sí, es normal. `README.md` (raíz) es el que ve GitHub al entrar al repo. `docs/README.md` es el índice interno de la carpeta de documentación (explica dónde está cada doc). Se dejan los dos; después actualizamos el de la raíz.

---

## 0) Antes de empezar — Preparación (2 min)

| Paso | Debería pasar |
|---|---|
| 1. Doble clic `setup_onedrive.bat` (o `py main.py` si es prueba local) | Crea `OneDrive\Academia\academia.db` y `fotos/`, `comprobantes/`, `BackupsAcademia` |
| 2. Abrir app → `admin / admin123` | Pide cambiar contraseña la primera vez. La ventana de cambio queda **al frente y centrada**, no se va al costado. El fondo muestra el Dashboard (no queda blanco). |
| 3. Cambiar a una clave nueva (6+ caracteres) | Dice “✅ Contraseña cambiada” y entra al Dashboard |

**Anota aquí si:** la ventana se esconde, queda en blanco, o no avisa.

---

## 1) Configuración (solo ADMIN) — Todo es configurable sin código

**Dónde:** `Sistema → Configuración` (7 secciones numeradas).

| Probar | Debería pasar | ¿Funciona? | ¿Falta / sin sentido? | Notas |
|---|---|---|---|---|
| 1. Editar `1. Información General` (nombre academia) → Guardar | Mensaje `✅ Se guardó` y al exportar Excel sale el nuevo nombre | | | |
| 2. En `2. Precios Flexibles` cambiar `Inscripción 100 → 120` → Guardar → crear alumno nuevo y matricular | La nueva matrícula usa `120` (no `100` viejo). La anterior sigue con `100`. | | | |
| 3. En `3. Mora y Vencimientos` activar mora `5%` y `Días por vencer 3` → Guardar | Cuotas vencidas suman mora y `Dashboard → Por vencer` avisa 3 días antes | | | |
| 4. En `4. Cuotas y Becas` desactivar `Permitir múltiples becas` → intentar matricular con 2 becas | Debe decir `No permite múltiples` | | | |
| 5. En `5. Respaldo` ver `Ruta OneDrive\BackupsAcademia` | `Sidebar → Respaldo` crea `academia_YYYY-MM-DD_HH-MM-SS.db` allí | | | |
| 6. En `6. Categorías` crear `3-5`, editar, desactivar | Aparece, se edita, se desactiva (no se borra) | | | |
| 7. En `7. Tipos Uniforme` crear `Uniforme Prueba` → desactivar | Aparece en `Inventario → Tipo uniforme` y luego desaparece al desactivar | | | |
| 8. En `8. Apariencia Visual` elegir `Grande` → Aplicar vista previa → Guardar → Reiniciar | Letra más grande (1.15x) y se mantiene tras reiniciar | | | |

> **No tiene sentido si:** un precio viejo cambia cuotas ya creadas (no debe), o si guarda sin mensaje `✅`.

---

## 2) Estudiantes + Foto + Apoderados (SECRETARIA puede, ADMIN también)

| Probar | Debería pasar | ¿Funciona? | ¿Falta? |
|---|---|---|---|
| 1. `Academia → Estudiantes → + Nuevo` → `DNI 8` o `CARNET 9`, nombres, `Fecha nacimiento` (escribir `2020-03-15` o combos + `Hoy`), sexo, dirección | Valida `8/9 dígitos`, si lo rompes dice `DNI debe tener 8` en rojo | | |
| 2. `Foto del niño (opcional) → Seleccionar foto` `jpg/png ≤2MB` | Label cambia a `foto.jpg`, al guardar copia a `OneDrive\Academia\fotos\DNI.jpg`. En la lista se ve **miniatura 60×60**, clic la amplía. | | | |
| 3. `Apoderado Principal` `DNI, nombres, parentesco` → `Guardar` | Mensaje `✅ Estudiante y apoderado registrados` y aparece en lista `Activos`. | | | |
| 4. Buscar por nombre/DNI + filtro `Activos/Retirados/Reingresantes` | Filtra al instante | | | |
| 5. `Editar` → cambiar foto → Guardar | Foto nueva reemplaza, `LOG` registra `foto_path` | | | |
| 6. `Retirar` (estado `ACTIVO`) → confirma | Pasa a `RETIRADO`, cierra matrícula `ACTIVO→RETIRADO` | | | |
| 7. `Reingreso` (estado `RETIRADO`) → `¿Vender uniforme?` → elegir `Entrenamiento 20` `Cantidad 1` → `Vender` | Pasa a `REINGRESANTE`, dialog vende uniforme (`stock-1`), si `Omitir` no vende. Luego `Matrículas` con `precio_reingreso 100` (más barato, sin camiseta auto). | | | |
| 8. `Apoderados` tab → `+ Asociar` → DNI existente → asociar como secundario (máx 2, 1 principal) → `Quitar` secundario OK, principal dice `No se puede desasociar principal` | Debe respetar `1 principal` único | | | |

> **Antes fallaba:** relación estudiante-apoderado permitía quedar sin principal o borrar principal. **Ahora corregido:** `estudiante_controller → apoderado_service` + `existe_relacion` + `marcar_principal`.

---

## 3) Matrículas (Inscripción vs Reingreso, diferir, descuentos)

| Probar | Debería pasar |
|---|---|
| 1. `Academia → Matrículas → + Nueva` → elige estudiante `ACTIVO/REINGRESANTE` (sugiere tarifa por edad) → `Tarifa`, `Monto pactado` vacío = `tarifa.monto`, `0` = gratuito, `Día vencimiento 5` | Si estudiante ya tiene `ACTIVO` dice `ya tiene matrícula activa`. |
| 2. `Pago diferido: 2 meses` → Registrar | Crea **2 cuotas** `PENDIENTE` correlativas `2026-09, 2026-10` (si `3` crea 3). `Ahora (0)` crea 1. |
| 3. `Beca` → 1 beca `25%` → Registrar | Cuota `120 → 90` (si `monto_pactado 90 + 25% → 67.5`). Si `permitir múltiples =0` y eliges 2 becas, bloquea. |
| 4. **Primera matrícula** (nuevo, `es_primera`) → verificar `Inventario → Camiseta Entrenamiento` | `Stock 50 → 49` automático + `Venta INSCRIPCION` `0 S/` + `movimiento SALIDA Inscripción` + `LOG`. Si `stock 0` dice `Stock insuficiente` y no crea matrícula. |
| 5. **Reingreso** (2ª matrícula tras retiro) | **No** descuenta stock; debe ir `Ventas → UNIFORME` manual `20` si quiere camiseta. Verificar `stock` queda `49`. |

> **Flexible:** todo precio/beca/diferir configurable; `monto_pactado is not None` no cae a tarifa.

---

## 4) Pagos y Cuotas (SECRETARIA)

| Probar | Debería pasar |
|---|---|
| 1. `Finanzas → Pagos → + Nuevo Pago` → `Estudiante` → `Cuota pendiente` (`2026-09 - S/90 PENDIENTE`) → `Monto 50` → `Método YAPE` → **si no subes comprobante** dice `Suba comprobante para YAPE...` naranja | Valida `comprobante_path` obligatorio si `≠EFECTIVO` → `OneDrive\Academia\comprobantes\{recibo}.jpg` |
| 2. Subir `jpg/png` → `label` muestra nombre → `Registrar Pago` | `✅ Pago registrado. Saldo: 40.00`, cuota pasa a `PARCIAL`, siguiente pago `40` → `PAGADO` genera siguiente mes automático `monto_base - mora`. |
| 3. `Filtros Fecha Inicio/Fin` (`YYYY-MM-DD` escribir o `Día/Mes/Año` click + `Hoy`) → `Buscar` | Filtra pagos; `Limpiar` borra fechas. Mensaje si `inicio>fin` rojo. |
| 4. `Morosos` tab → `Actualizar` | Lista `Cuotas vencidas` `Venció: 2026-08-10 Saldo: 90` si las hay, sino `No hay cuotas vencidas` verde. |
| 5. Historial `Buscar por recibo` | Filtra `R2026...` al vuelo. |

> **Vacío:** antes `label_form_status` no existía y la vista quedaba blanca. Ahora `Historial`, `Registrar Pago`, `Morosos` siempre tienen header `💰` + filtros con `🔍` y estado `⏳ Cargando...` / `📭 No se encontraron` + guía `+ Nuevo Pago`.

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
