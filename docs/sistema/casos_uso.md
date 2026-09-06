# Casos de Uso

> **v2 (2026-09):** + foto estudiante `RN-041`, comprobante `RN-042`, diferir 2-3 meses `RN-043`, tipos uniforme `RN-039`, ventas `RN-038/040`, egresos `RN-046`, precios flexibles `RN-047` (ver `sistema/reglas_negocio.md`).

## Actores

### ADMIN

Puede acceder a todas las funcionalidades del sistema.

Responsabilidades:

* Gestión de usuarios
* Configuración del sistema
* Auditoría
* Backups y restauración
* Gestión de categorías
* Gestión de tarifas
* Gestión de becas
* Reportes

---

### SECRETARIA

Responsable de las operaciones diarias.

Responsabilidades:

* Registro de estudiantes
* Registro de apoderados
* Gestión de matrículas
* Registro de pagos
* Gestión de inventario
* Consulta de reportes permitidos

---

# CU-001 Iniciar Sesión

## Actor

* ADMIN
* SECRETARIA

## Flujo Principal

1. Ingresar usuario.
2. Ingresar contraseña.
3. Validar credenciales.
4. Mostrar dashboard correspondiente.

## Reglas Relacionadas

* RN-002
* RN-033

---

# CU-002 Registrar Persona

## Actor

* SECRETARIA
* ADMIN

## Flujo Principal

1. Ingresar DNI.
2. Ingresar nombres.
3. Ingresar apellidos.
4. Registrar datos de contacto.
5. Guardar información.

## Validaciones

* DNI único.
* Nombres obligatorios.
* Apellidos obligatorios.

## Reglas Relacionadas

* RN-001

---

# CU-003 Registrar Apoderado

## Actor

* SECRETARIA
* ADMIN

## Flujo Principal

1. Buscar persona existente o registrar nueva.
2. Registrar parentesco.
3. Registrar ocupación.
4. Guardar apoderado.

## Reglas Relacionadas

* RN-004

---

# CU-004 Registrar Estudiante (v2: + foto)

## Actor

* SECRETARIA
* ADMIN

## Flujo Principal

1. Buscar persona existente o registrar nueva (DNI/CARNET).
2. Registrar estudiante + foto opcional `jpg/png ≤2MB` → `OneDrive\Academia\fotos\{DNI}.jpg` (`RN-041`).
3. Asociar apoderado principal (DNI/CARNET, parentesco).
4. Asociar apoderados secundarios (opcional, máx 2).
5. Guardar registro.

## Reglas Relacionadas

* RN-003
* RN-005
* RN-041

---

# CU-005 Registrar Matrícula (v2: diferir + inscripción -1 camiseta)

## Actor

* SECRETARIA
* ADMIN

## Flujo Principal

1. Seleccionar estudiante (nuevo o reingresante).
2. Seleccionar tarifa (sugerida por edad).
3. Definir monto pactado (opcional, `0` gratuito).
4. Definir día vencimiento `1-31`.
5. Elegir diferir `0/2/3 meses` (`RN-043`) → genera N cuotas `PENDIENTE`.
6. Asignar becas (PORCENTAJE/MONTO_FIJO, múltiple si `permitir_multiples_becas=1`).
7. Crear matrícula → si es **primera** descuenta `1 Camiseta Entrenamiento` `stock-1` `venta INSCRIPCION` (`RN-036`), si es **reingreso** va por `CU-006` + venta separada.
8. Generar cuota(s).

## Reglas Relacionadas

* RN-008, RN-010, RN-011, RN-012, RN-014
* RN-036, RN-037, RN-043, RN-047

---

# CU-006 Registrar Reingreso

## Actor

* SECRETARIA
* ADMIN

## Flujo Principal

1. Buscar estudiante retirado.
2. Registrar nueva matrícula.
3. Mantener historial de matrículas anteriores.
4. Generar nueva cuota.

## Reglas Relacionadas

* RN-009

---

# CU-007 Consultar Cuotas

## Actor

* SECRETARIA
* ADMIN

## Flujo Principal

1. Buscar estudiante.
2. Visualizar cuotas.
3. Mostrar estado actual.
4. Mostrar saldo pendiente.

## Reglas Relacionadas

* RN-015
* RN-018

---

# CU-008 Registrar Pago (v2: + comprobante OneDrive)

## Actor

* SECRETARIA
* ADMIN

## Flujo Principal

1. Buscar estudiante → cuotas pendientes.
2. Seleccionar cuota.
3. Ingresar monto (completo/parcial).
4. Seleccionar método `EFECTIVO/YAPE/PLIN/TRANSFERENCIA` + **subir comprobante** `jpg/png` si `≠EFECTIVO` → `OneDrive\Academia\comprobantes\{recibo}.jpg` (`RN-042`).
5. Registrar pago → `transaccion` + recálculo `saldo` + `LOG`.
6. Actualizar saldo `PENDIENTE→PARCIAL→PAGADO` + siguiente cuota auto `RN-014`.
7. Generar comprobante interno `RYYYYMMDD...`.

## Reglas Relacionadas

* RN-016, RN-017, RN-018, RN-022, RN-023, RN-042

---

# CU-009 Consultar Morosos

## Actor

* SECRETARIA
* ADMIN

## Flujo Principal

1. Consultar cuotas vencidas.
2. Mostrar estudiantes con saldo pendiente.
3. Mostrar monto adeudado.
4. Mostrar fecha de vencimiento.

## Reglas Relacionadas

* RN-019
* RN-020

---

# CU-010 Registrar Movimiento de Inventario

## Actor

* SECRETARIA
* ADMIN

## Flujo Principal

1. Seleccionar producto.
2. Seleccionar tipo de movimiento.
3. Ingresar cantidad.
4. Registrar motivo.
5. Actualizar stock.

## Reglas Relacionadas

* RN-024
* RN-027

---

# CU-011 Registrar Producto

## Actor

* SECRETARIA
* ADMIN

## Flujo Principal

1. Seleccionar categoría.
2. Registrar código.
3. Registrar nombre.
4. Definir stock mínimo.
5. Definir tipo de uso.
6. Guardar producto.

## Reglas Relacionadas

* RN-025
* RN-026

---

# CU-012 Generar Reportes

## Actor

* SECRETARIA
* ADMIN

## Reportes Iniciales

* Morosos
* Pagos por fecha
* Ingresos mensuales
* Alumnos por categoría
* Inventario
* Becas activas

---

# CU-013 Gestionar Usuarios

## Actor

* ADMIN

## Flujo Principal

1. Crear usuario.
2. Editar usuario.
3. Activar usuario.
4. Desactivar usuario.
5. Restablecer contraseña.

## Reglas Relacionadas

* RN-002

---

# CU-014 Configurar Sistema

## Actor

* ADMIN

## Flujo Principal

1. Configurar mora.
2. Configurar días por vencer.
3. Configurar becas.
4. Configurar backups.
5. Guardar cambios.

## Reglas Relacionadas

* RN-020
* RN-021
* RN-029

---

# CU-015 Consultar Auditoría

## Actor

* ADMIN

## Flujo Principal

1. Abrir módulo de auditoría.
2. Filtrar registros.
3. Consultar cambios realizados.
4. Exportar resultados (opcional).

## Restricciones

* Solo lectura.
* No se permite modificar registros.

## Reglas Relacionadas

* RN-032
* RN-034
* RN-035

---

# CU-016 Crear Backup

## Actor

* ADMIN

## Flujo Principal

1. Seleccionar ubicación.
2. Ejecutar respaldo.
3. Confirmar creación.

## Reglas Relacionadas

* RN-030

---

# CU-017 Restaurar Backup

## Actor

* ADMIN

## Flujo Principal

1. Seleccionar archivo de respaldo.
2. Confirmar restauración.
3. Reemplazar base de datos actual.
4. Reiniciar sistema.

## Reglas Relacionadas

* RN-030

---

# CU-018 Dashboard (v2: + ventas/egresos/nuevos)

## Actor

* ADMIN
* SECRETARIA

## Información Mostrada (14 cards)

* Alumnos activos, Cuotas vencidas/por vencer, Pagos/Ingresos hoy/mes, Monto vencido/por vencer, Stock bajo
* **v2:** Ventas mes, Egresos mes, Neto mes, Nuevos/Antiguos mes, Total matrículas

## Reglas Relacionadas

* RN-021, RN-031, RN-045/046/049

---

# CU-019 Registrar Venta (v2)

## Actor

* SECRETARIA, ADMIN

## Flujo Principal

1. Seleccionar producto por `tipo_uniforme` (Entrenamiento/Competencia/Completo/Media) o tienda.
2. Cantidad + `tipo_venta` `UNIFORME/TIENDA/CAMPEONATO/INSCRIPCION` + método + comprobante OneDrive.
3. Validar `stock>=cantidad`, calcular `precio_venta` o `monto_total` pactado (descuento flexible).
4. `transaccion` `stock- cant` + `detalle_venta` + `movimiento SALIDA` + `LOG venta`.

## Reglas Relacionadas

* RN-038, RN-039, RN-040, RN-042

---

# CU-020 Registrar Egreso (v2)

## Actor

* ADMIN

## Flujo Principal

1. Concepto `PROFESOR/PERSONAL/CAMPEONATO_FIJO/ARBITRAJE/VIATICOS` + monto>0 + fecha + responsable.
2. Guardar → `LOG egreso`, `reporte ingresos vs egresos` = `pagos+ventas - egresos`.

## Reglas Relacionadas

* RN-046, RN-047/049
