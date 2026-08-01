# Plan de Sprints

## Duración Recomendada

Cada sprint tendrá una duración de:

```text
1 semana
```

---

# Sprint 1 - Base de Datos

## Objetivo

Implementar toda la infraestructura de persistencia.

## Tareas

### Database

* connection.py
* create_db.py
* seed.py
* backup.py
* restore.py

### Base de Datos

* Creación de tablas
* Índices
* Restricciones
* Datos iniciales

### Modelos

* Todas las entidades con @dataclass

## Entregables

* Base de datos funcional
* Creación automática
* Usuario administrador inicial

---

# Sprint 2 - Seguridad

## Objetivo

Implementar autenticación y control de acceso.

## Tareas

### Usuarios

* CRUD usuarios
* Activación y desactivación

### Login

* Inicio de sesión
* Cierre de sesión
* Cambio de contraseña

### Roles

* ADMIN
* SECRETARIA

## Entregables

* Acceso seguro al sistema

---

# Sprint 3 - Gestión Académica

## Objetivo

Gestionar estudiantes y apoderados.

## Tareas

### Personas

* Registro
* Edición
* Consulta

### Apoderados

* Registro
* Asociación

### Estudiantes

* Registro
* Edición
* Consulta

### Relaciones

* Estudiante-Apoderado

## Entregables

* Módulo académico operativo

---

# Sprint 4 - Matrículas

## Objetivo

Gestionar permanencia de estudiantes.

## Tareas

### Matrículas

* Registro
* Reingresos
* Becas
* Montos pactados

### Cuotas

* Generación inicial
* Estados

## Entregables

* Sistema de matrículas funcional

---

# Sprint 5 - Pagos

## Objetivo

Implementar control financiero.

## Tareas

### Pagos

* Registro de pagos
* Pagos parciales
* Métodos de pago

### Cuotas

* Actualización automática
* Saldos
* Morosos

### Comprobantes

* Generación interna

## Entregables

* Sistema de pagos operativo

---

# Sprint 6 - Inventario

## Objetivo

Implementar control de insumos.

## Tareas

### Categorías

* CRUD categorías

### Productos

* CRUD productos

### Movimientos

* Entradas
* Salidas
* Ajustes

### Stock

* Control mínimo

## Entregables

* Inventario funcional

---

# Sprint 7 - Dashboard

## Objetivo

Implementar indicadores principales.

## Tareas

### Dashboard

* Alumnos activos
* Cuotas vencidas
* Cuotas por vencer
* Pagos del día
* Ingresos del mes
* Stock bajo

## Entregables

* Dashboard operativo

---

# Sprint 8 - Reportes

## Objetivo

Implementar exportación de información.

## Tareas

### Excel

* Morosos
* Pagos por fecha
* Ingresos mensuales
* Alumnos por categoría
* Inventario
* Becas activas

## Entregables

* Reportes exportables

---

# Sprint 9 - Configuración

## Objetivo

Implementar administración del sistema.

## Tareas

### Configuración

* Mora
* Días por vencer
* Backups
* Parámetros generales

### Auditoría

* Consulta de logs
* Filtros

## Entregables

* Panel administrativo completo

---

# Sprint 10 - Estabilización

## Objetivo

Preparar la versión final.

## Tareas

### Calidad

* Corrección de errores
* Optimización

### Pruebas

* Casos de uso
* Pruebas integrales

### Documentación

* Actualización final

## Entregables

* Versión 1.0 estable

---

**Estado actual:** Ver `docs/sprint10_plan.md` para plan detallado
