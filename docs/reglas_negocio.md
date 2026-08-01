# Reglas de Negocio

## Objetivo

Este documento define las reglas de funcionamiento del sistema de gestión de la academia.

Las reglas aquí descritas deben respetarse tanto en la base de datos como en la lógica de negocio de la aplicación.

---

# RN-001 Registro de Personas

Toda persona registrada en el sistema deberá tener un DNI único.

No se permitirá registrar dos personas con el mismo DNI.

---

# RN-002 Usuarios del Sistema

Los únicos roles disponibles son:

* ADMIN
* SECRETARIA

No se permitirá crear usuarios con otros roles.

Cada persona podrá tener como máximo un usuario asociado.

---

# RN-003 Registro de Estudiantes

Todo estudiante deberá estar asociado a un registro de persona.

No se permitirá crear estudiantes sin una persona asociada.

---

# RN-004 Registro de Apoderados

Todo apoderado deberá estar asociado a un registro de persona.

Los datos de contacto podrán completarse posteriormente si aún no se conocen.

---

# RN-005 Relación Estudiante - Apoderado

Todo estudiante deberá tener al menos un apoderado principal.

Un estudiante podrá tener múltiples apoderados.

Solo uno de ellos podrá estar marcado como principal.

---

# RN-006 Categorías

Las categorías representan rangos de edad.

Ejemplos:

* 3-5
* 6-8
* 9-12
* 13-15
* 16-18

Las categorías podrán activarse o desactivarse sin eliminar registros históricos.

---

# RN-007 Tarifas

Las tarifas estarán asociadas a una categoría.

Una categoría podrá tener múltiples tarifas a lo largo del tiempo.

Las tarifas históricas no deberán modificarse una vez utilizadas por una matrícula.

---

# RN-008 Matrículas

Toda matrícula deberá estar asociada a:

* Un estudiante
* Una tarifa

Una matrícula representa un periodo de permanencia del estudiante en la academia.

---

# RN-009 Reingreso de Estudiantes

Cuando un estudiante regrese a la academia después de retirarse:

* No se reactivará una matrícula anterior.
* Se creará una nueva matrícula.

De esta forma se conserva el historial completo.

---

# RN-010 Monto Pactado

La tarifa oficial podrá ser modificada mediante un monto pactado específico para un estudiante.

Ejemplo:

Tarifa oficial:

S/120

Monto pactado:

S/90

Las cuotas generadas deberán utilizar el monto pactado cuando exista.

---

# RN-011 Becas

Las becas pueden ser de dos tipos:

* PORCENTAJE
* MONTO_FIJO

Las becas se asignarán a través de la tabla MATRICULA_BECA.

---

# RN-012 Múltiples Becas

La posibilidad de asignar múltiples becas dependerá de la configuración del sistema.

Parámetro:

permitir_multiples_becas

Valores:

* 1 = permitido
* 0 = no permitido

---

# RN-013 Cuotas

Las cuotas serán exclusivamente mensuales.

No se manejarán cuotas semanales ni quincenales.

---

# RN-014 Generación de Cuotas

Al registrar una matrícula:

* No se generarán cuotas de todo el año.
* Solo se generará la siguiente cuota pendiente.

Las cuotas posteriores podrán generarse automáticamente mediante procesos internos del sistema.

---

# RN-015 Estados de Cuota

Una cuota podrá encontrarse en uno de los siguientes estados:

* PENDIENTE
* PARCIAL
* PAGADO
* VENCIDO

---

# RN-016 Pago Parcial

Cuando una cuota reciba un pago menor al monto total:

Estado:

PARCIAL

Ejemplo:

Monto total:

S/120

Pagado:

S/50

Saldo:

S/70

Estado:

PARCIAL

---

# RN-017 Pago Completo

Cuando el saldo de una cuota sea igual a cero:

Estado:

PAGADO

---

# RN-018 Saldo de Cuota

El saldo de una cuota se calculará mediante:

Saldo = Monto Total - Monto Pagado

El saldo nunca podrá ser negativo.

---

# RN-019 Cuotas Vencidas

Una cuota se considerará vencida cuando:

Fecha actual > Fecha de vencimiento

Y el saldo sea mayor que cero.

---

# RN-020 Mora

Inicialmente el sistema trabajará con:

mora_habilitada = 0

No se aplicarán intereses ni recargos automáticos.

La funcionalidad quedará preparada para futuras versiones.

---

# RN-021 Alertas de Vencimiento

El sistema deberá identificar cuotas próximas a vencer.

La cantidad de días será configurable mediante:

dias_por_vencer

Ejemplo:

dias_por_vencer = 3

Las cuotas con vencimiento dentro de los próximos tres días deberán mostrarse como "Por vencer".

---

# RN-022 Pagos

Todo pago deberá generar un comprobante interno del sistema.

No se emitirán comprobantes electrónicos SUNAT en la versión inicial.

---

# RN-023 Métodos de Pago

Métodos permitidos:

* EFECTIVO
* YAPE
* PLIN
* TRANSFERENCIA

---

# RN-024 Registro de Inventario

Todos los movimientos de inventario deberán quedar registrados.

No se permitirá eliminar movimientos históricos.

---

# RN-025 Categorías de Productos

Inicialmente existirán las siguientes categorías:

* INSUMO_DEPORTIVO
* INSUMO_ALIMENTO

Podrán añadirse nuevas categorías en el futuro.

---

# RN-026 Tipo de Uso de Productos

Los productos podrán clasificarse como:

* CONSUMO_INTERNO
* VENTA

Inicialmente la academia utilizará principalmente consumo interno.

---

# RN-027 Control de Stock

El stock actual se almacenará en la tabla PRODUCTO.

Cada movimiento de inventario deberá actualizar dicho valor.

---

# RN-028 Soft Delete

No se realizarán eliminaciones físicas de registros.

La baja lógica se realizará mediante:

activo = 0

---

# RN-029 Configuración del Sistema

Los parámetros operativos deberán administrarse desde el panel de configuración del ADMIN.

No será necesario modificar código para cambiar:

* Mora
* Días por vencer
* Backups
* Becas
* Parámetros generales

---

# RN-030 Backups

El sistema permitirá:

* Backup manual en cualquier momento.
* Backup automático semanal.

La frecuencia se almacenará en la tabla CONFIGURACION.

---

# RN-031 Dashboard de Secretaria

Al iniciar sesión, la secretaria deberá visualizar como mínimo:

* Alumnos activos
* Cuotas vencidas
* Cuotas por vencer
* Pagos del día
* Ingresos del mes
* Stock bajo

---

# RN-032 Auditoría

Toda operación importante deberá registrarse en el LOG.

Ejemplos:

* INSERT
* UPDATE
* DESACTIVACIÓN

El sistema almacenará:

* Usuario
* Tabla afectada
* Registro afectado
* Valor anterior
* Valor nuevo
* Fecha y hora

---

# RN-033 Seguridad

La contraseña del usuario administrador inicial deberá cambiarse obligatoriamente después del primer acceso.

Usuario inicial:

admin

Contraseña inicial:

admin123

# RN-034 Acceso a Auditoría

El módulo de auditoría será accesible únicamente para usuarios con rol ADMIN.

Los usuarios con rol SECRETARIA no podrán:

- Consultar registros de auditoría.
- Visualizar cambios históricos.
- Exportar registros de auditoría.
- Modificar registros de auditoría.

Los registros de auditoría son de solo lectura incluso para el ADMIN.

# RN-035 Inmutabilidad de Auditoría

Los registros almacenados en LOG no podrán ser editados ni eliminados desde la aplicación.

Toda entrada de auditoría será considerada evidencia histórica del sistema.