# Roadmap del Proyecto

> **v2 entregada 2026-09 (flexible + OneDrive):** `tipo_uniforme/venta/egreso`, `estudiante.foto`, `comprobante OneDrive`, `precio_*` configurables, `diferir 2-3` cuotas, dashboard 14 cards, 9 reportes. Ver `desarrollo/cambios_RN_v2.md`.

## Objetivo

Desarrollar un sistema de gestión para academia deportiva que permita administrar estudiantes, matrículas, pagos, inventario, reportes y configuración del sistema.

---

# Versión 1.0 - Base Operativa

## Gestión Académica

* Registro de personas
* Registro de apoderados
* Registro de estudiantes
* Relación estudiante-apoderado
* Categorías
* Tarifas
* Matrículas
* Reingresos

## Gestión de Pagos

* Generación de cuotas
* Pagos completos
* Pagos parciales
* Control de saldos
* Comprobantes internos

## Inventario

* Categorías de productos
* Registro de productos
* Movimientos de inventario
* Control de stock mínimo

## Seguridad

* Login
* Roles ADMIN y SECRETARIA
* Cambio obligatorio de contraseña inicial

## Configuración

* Parámetros generales
* Mora habilitada/deshabilitada
* Días por vencer
* Configuración de backups

## Auditoría

* Registro de operaciones
* Consulta de auditoría para ADMIN

## Reportes

* Morosos
* Pagos por fecha
* Ingresos mensuales
* Alumnos por categoría
* Inventario
* Becas activas

---

# Versión 1.1 - Mejoras Administrativas

## Pagos

* Adelantos de cuotas
* Mejor visualización de estados de pago
* Historial consolidado de pagos

## Inventario

* Alertas de stock bajo
* Exportación de movimientos

## Reportes

* Nuevos filtros
* Exportación mejorada

---

# Versión 1.2 - Integraciones

## OneDrive

* Sincronización automática de backups
* Restauración desde respaldo remoto

## Notificaciones

* Alertas de cuotas por vencer
* Alertas de morosidad

---

# Versión 1.3b - v2.1 Documentada (2026-09-06) — es_nuevo + conceptos sin redundancia + secretaria ampliada

- `estudiante.es_nuevo` checkbox única vez en `Estudiantes → Nuevo` (para cargas masivas de existentes), primera matrícula si `es_nuevo=1` regala `Camiseta Entrenamiento S/0` atomico + bloquea extras (RN-051)
- `concepto_cobro`+`concepto_item` catálogo flexible con títulos e ítems incluidos, sin duplicar `configuracion.precio_*` (fallback) ni `tarifa` — precedencia definida en `plan_dayanna_v2.1.md:1.2` (RN-052)
- Secretaria: `egresos crear/editar` permitido, `restaurar/rotar backup` y `auditoría/config` siguen ADMIN (matriz `plan_dayanna_v2.1.md:1.3`)
- Backups `UTC-5`, tipos uniforme solo nombre, reingresantes en Activos, matrícula `-1/+1` totales fijos + MessageBox, reporte regalos mensual, dashboard `Nuevos`

# Versión 1.3 - v2 Entregada (2026-09) — Flexible + OneDrive

## Comercial flexible

* Venta `UNIFORME/TIENDA/CAMPEONATO/INSCRIPCION` (`tipo_uniforme` 4, `producto.precio_compra/venta`)
* Egresos `PROFESOR/PERSONAL/CAMPEONATO` + reporte `Ingresos vs Egresos neto`
* Inscripción primera matrícula `-1 Camiseta` (reingreso via venta)

## Operación central

* BD `OneDrive\Academia\academia.db` via `config.ini` (`setup_onedrive.bat`), `FOTOS_DIR/COMPROBANTES_DIR` OneDrive, backup `BackupsAcademia`
* Dashboard 14 cards (`Ventas/Egresos/Neto/Nuevos vs Antiguos`), fotos thumbnail 60, comprobantes

## UX

* Menú 5 grupos, `DatePicker` escribir/clickear, mensajes `✅/⏳/❌`, sidebar scrolleable, visual `font_scale` en `Configuración`

---

# Versión 2.0 - Comercial (plan futuro)

## Ventas

* Venta de productos (ya entregado v1.3)
* Control de ingresos por ventas (ya)
* Historial de ventas (ya)

## Producción

* Producción de panes
* Producción de alimentos
* Consumo de insumos

## Reportes Avanzados

* Rentabilidad
* Costos operativos
* Estadísticas históricas

---

# Versión 3.0 - Expansión

## Multi-Sede

* Gestión de múltiples academias
* Inventario por sede
* Reportes por sede

## Plataforma Web

* Portal administrativo web
* Acceso remoto

## Aplicación Móvil

* Consulta de pagos
* Consulta de asistencia
* Notificaciones a apoderados
