# Diseño de Base de Datos y Arquitectura - Academia de Fútbol

## Objetivo

Sistema local para gestión de:

- Estudiantes
- Apoderados
- Pagos y cuotas
- Becas
- Matrículas y reingresos
- Inventario
- Usuarios y roles
- Reportes Excel
- Backups y restauración
- Auditoría (logs)

---

# Arquitectura General

```text
Views
    ↓
Controllers
    ↓
Services
    ↓
Repositories
    ↓
Database (SQLite)
```

---

# Estructura de Tablas

```text
persona
usuario

apoderado
estudiante
estudiante_apoderado

categoria
tarifa

beca
matricula
matricula_beca

cuota
pago
detalle_pago

categoria_producto
producto
movimiento_inventario

configuracion
log
```

---

# Relación de Entidades

```text
PERSONA
│
├── USUARIO
│
├── APODERADO
│
└── ESTUDIANTE
         │
         ├── ESTUDIANTE_APODERADO
         │         │
         │         └── APODERADO
         │
         └── MATRICULA
                   │
                   ├── TARIFA
                   │       │
                   │       └── CATEGORIA
                   │
                   ├── MATRICULA_BECA
                   │          │
                   │          └── BECA
                   │
                   └── CUOTA
                             │
                             └── DETALLE_PAGO
                                         │
                                         └── PAGO

CATEGORIA_PRODUCTO
        │
        └── PRODUCTO
                    │
                    └── MOVIMIENTO_INVENTARIO

CONFIGURACION

LOG
```

---

# Tabla PERSONA

Datos generales reutilizables.

Campos:

- id_persona
- dni (UNIQUE)
- nombres
- apellidos
- fecha_nacimiento
- sexo
- direccion
- telefono
- correo
- activo
- fecha_creacion
- fecha_actualizacion

---

# Tabla USUARIO

Campos:

- id_usuario
- id_persona
- username
- password_hash
- rol
- activo
- fecha_creacion
- fecha_actualizacion

Roles:

- ADMIN
- SECRETARIA

---

# Tabla APODERADO

Campos:

- id_apoderado
- id_persona
- parentesco
- ocupacion
- activo
- fecha_creacion
- fecha_actualizacion

Relación:

- Un apoderado puede tener varios estudiantes.

---

# Tabla CATEGORIA

Campos:

- id_categoria
- nombre
- edad_min
- edad_max
- activo

Ejemplos:

- 3-5
- 6-8
- 9-12
- 13-15

---

# Tabla TARIFA

Permite mantener historial de precios.

Campos:

- id_tarifa
- id_categoria
- nombre
- monto
- fecha_inicio
- fecha_fin
- activo

Ejemplo:

Sub-8:

- 2026 → S/120
- 2027 → S/140

---

# Tabla BECA

Catálogo de becas y descuentos disponibles.

Campos:

- id_beca
- nombre
- tipo
- valor
- observacion
- activo

Tipos:

- PORCENTAJE
- MONTO_FIJO

Ejemplos:

- 25%
- 50%
- S/40

Observaciones:

- Una beca puede ser utilizada por múltiples matrículas.
- Una matrícula puede tener cero, una o varias becas.
- La asignación se realiza mediante la tabla `matricula_beca`.

---

# Tabla MATRICULA

Permite mantener historial de matrículas y reingresos.

Campos:

- id_matricula
- id_estudiante
- id_tarifa
- monto_pactado
- fecha_inicio
- fecha_fin
- dia_vencimiento
- estado
- activo

Ejemplo:

Alumno ingresa → Matrícula 1

Se retira

Reingresa → Matrícula 2

Observaciones:

- Una matrícula puede tener múltiples becas.
- El monto de las cuotas se calcula utilizando la tarifa asociada y las becas vigentes de la matrícula.

---

# Tabla MATRICULA_BECA

Tabla intermedia para la relación entre matrículas y becas.

Campos:

- id_matricula_beca
- id_matricula
- id_beca
- fecha_asignacion
- activo

Relaciones:

- Una matrícula puede tener varias becas.
- Una beca puede estar asociada a varias matrículas.

Ejemplo:

Matrícula 15

↓

- Beca Deportiva (25%)
- Beca Hermano (S/20)

---

# Tabla ESTUDIANTE

Campos:

- id_estudiante
- id_persona
- estado
- fecha_ingreso
- fecha_retiro
- activo

Estados:

- ACTIVO
- RETIRADO
- REINGRESANTE

---

# Tabla ESTUDIANTE_APODERADO

Permite múltiples apoderados por estudiante.

Campos:

- id_estudiante_apoderado
- id_estudiante
- id_apoderado
- es_principal
- activo

Reglas:

- Todo estudiante debe tener un apoderado principal.
- Solo puede existir un apoderado principal por estudiante.
- Puede existir más de un apoderado secundario.

---

# Tabla CUOTA

Representa cada período de pago.

Campos:

- id_cuota
- id_matricula
- periodo
- fecha_vencimiento
- monto_total
- monto_pagado
- saldo
- estado
- activo

Estados:

- PENDIENTE
- PARCIAL
- PAGADO
- VENCIDO

Importante:

NO almacenar:

- Al día
- Por vencer
- Vencido

como datos permanentes.

Deben calcularse dinámicamente.

---

# Tabla PAGO

Representa una transacción.

Campos:

- id_pago
- numero_recibo
- fecha_pago
- monto_total
- metodo_pago
- observacion
- activo

---

# Tabla DETALLE_PAGO

Permite que un pago cubra varias cuotas.

Campos:

- id_detalle_pago
- id_pago
- id_cuota
- monto_pagado

Ejemplo:

Pago de S/360

Cubre:

- Julio
- Agosto
- Septiembre

---

# Tabla PRODUCTO

Campos:

- id_producto
- codigo
- nombre
- stock_actual
- stock_minimo
- precio
- activo
- id_categoria_producto
- tipo_uso

No eliminar productos.

Usar activo = 0.

---

# Tabla CATEGORIA_PRODUCTO

Clasifica productos de inventario.

Campos:

- id_categoria_producto
- nombre
- activo

Valores iniciales:

- INSUMO_DEPORTIVO
- INSUMO_ALIMENTO

---

# Tabla MOVIMIENTO_INVENTARIO

Campos:

- id_movimiento
- id_producto
- id_usuario
- tipo_movimiento
- cantidad
- fecha_movimiento
- motivo

Tipos:

- ENTRADA
- SALIDA
- AJUSTE

Nunca eliminar movimientos.

---

# Tabla CONFIGURACION

- id_configuracion

- nombre_academia
- direccion
- telefono
- correo

- mora_habilitada
- porcentaje_mora

- dias_por_vencer

- permitir_multiples_becas

- backup_automatico
- frecuencia_backup

- ruta_backup
- correo_onedrive

- fecha_actualizacion

---

# Tabla LOG

Auditoría.

Campos:

- id_log

- id_usuario

- tabla_afectada
- id_registro

- accion

- valor_anterior
- valor_nuevo

- fecha

Ejemplos:

- Registró pago
- Eliminó usuario
- Restauró backup
- Actualizó inventario

---

# Reglas Importantes

## Estado de Pago

No almacenar:

- Al día
- Por vencer
- Vencido

Calcular usando:

- Fecha actual
- Fecha vencimiento
- Estado de cuota

---

## Edad

No almacenar edad.

Almacenar:

- fecha_nacimiento

Calcular edad dinámicamente.

---

## Soft Delete

Preferir:

- activo = 0

en lugar de eliminar registros.

Aplicar en:

- estudiante
- usuario
- producto
- beca
- tarifa
- categoria

---

# Inventario

No modificar stock sin registro.

Todo cambio debe generar:

MOVIMIENTO_INVENTARIO

---

# Reportes Excel

No crear tablas específicas.

Generar desde consultas SQL.

Reportes previstos:

- Pagos del mes
- Alumnos morosos
- Alumnos por categoría
- Inventario actual
- Movimientos de inventario
- Ingresos mensuales
- Becas activas

---

# Backups

Carpeta:

```text
backups/
```

Formato:

```text
academia_YYYY-MM-DD_HH-MM.db
```

Funciones:

- Backup manual
- Backup automático
- Restauración desde interfaz

---

# Seguridad

ADMIN:

- Crear usuarios
- Restaurar backups
- Modificar configuraciones
- Eliminar registros

SECRETARIA:

- Registrar estudiantes
- Registrar pagos
- Registrar inventario
- Exportar Excel


# Regla de aplicación de becas

Las becas se aplicarán en el orden en que fueron asignadas a la matrícula.

Tipos soportados:

1. PORCENTAJE
2. MONTO_FIJO

Ejemplo:

Tarifa: S/120

Beca Deportiva: 25%
→ S/90

Beca Hermano: S/20
→ S/70

Monto final de cuota: S/70

---

# Sprint 1

## Backend

- connection.py
- create_db.py
- creación de tablas
- usuario administrador inicial
- categorías iniciales
- tarifas iniciales
- índices

## Utilidades

- backup.py
- restore.py

## Validación

- DB Browser for SQLite
- pruebas CRUD básicas

---

# Próximos Sprint

Sprint 2:

- Models
- Repositories
- Services
- Login funcional

Sprint 3:

- Gestión de estudiantes
- Matrículas
- Becas

Sprint 4:

- Pagos y cuotas

Sprint 5:

- Inventario

Sprint 6:

- Reportes Excel

Sprint 7:

- Dashboard y estadísticas
