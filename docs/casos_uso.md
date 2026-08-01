# Casos de Uso

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

# CU-004 Registrar Estudiante

## Actor

* SECRETARIA
* ADMIN

## Flujo Principal

1. Buscar persona existente o registrar nueva.
2. Registrar estudiante.
3. Asociar apoderado principal.
4. Asociar apoderados secundarios (opcional).
5. Guardar registro.

## Reglas Relacionadas

* RN-003
* RN-005

---

# CU-005 Registrar Matrícula

## Actor

* SECRETARIA
* ADMIN

## Flujo Principal

1. Seleccionar estudiante.
2. Seleccionar tarifa.
3. Definir monto pactado (opcional).
4. Definir día de vencimiento.
5. Asignar becas (si corresponde).
6. Crear matrícula.
7. Generar primera cuota.

## Reglas Relacionadas

* RN-008
* RN-010
* RN-011
* RN-012
* RN-014

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

# CU-008 Registrar Pago

## Actor

* SECRETARIA
* ADMIN

## Flujo Principal

1. Buscar estudiante.
2. Seleccionar cuota.
3. Ingresar monto recibido.
4. Seleccionar método de pago.
5. Registrar pago.
6. Actualizar saldo.
7. Generar comprobante interno.

## Reglas Relacionadas

* RN-016
* RN-017
* RN-018
* RN-022
* RN-023

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

# CU-018 Dashboard

## Actor

* ADMIN
* SECRETARIA

## Información Mostrada

* Alumnos activos
* Cuotas vencidas
* Cuotas por vencer
* Pagos del día
* Ingresos del mes
* Stock bajo

## Reglas Relacionadas

* RN-021
* RN-031
