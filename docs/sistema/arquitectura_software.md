# Arquitectura de Software

> **Actualización v2 (2026-09):** BD central OneDrive `OneDrive\Academia\academia.db` via `utils/constants.py:72` `config.ini` + `tipo_uniforme/venta/detalle_venta/egreso` + `FOTOS_DIR/COMPROBANTES_DIR` + 9 reportes. Estructura base sin cambios, solo extensión flexible (precios/becas/OneDrive).

## Objetivo

Definir la estructura técnica del sistema de gestión de academia, estableciendo la organización del código, responsabilidades de cada capa y flujo de comunicación entre componentes.

---

# Tecnologías

## Lenguaje

```text
Python 3.x
```

## Base de Datos

```text
SQLite
```

## Interfaz Gráfica

```text
CustomTkinter
```

## Reportes

```text
openpyxl
```

## Control de Versiones

```text
Git
GitHub
```

---

# Arquitectura General

El sistema seguirá una arquitectura por capas.

```text
┌─────────────────┐
│      Views      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Controllers   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Services     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Repositories   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     SQLite      │
└─────────────────┘
```

---

# Flujo de Operación

Ejemplo: Registrar Pago

```text
PagoView

↓
PagoController

↓
PagoService

↓
PagoRepository

↓
SQLite
```

---

# Responsabilidades por Capa

## Views

Responsables de la interacción con el usuario.

Funciones:

* Mostrar formularios.
* Mostrar tablas.
* Mostrar reportes.
* Mostrar mensajes de error.
* Capturar acciones del usuario.

No deben:

* Ejecutar SQL.
* Aplicar reglas de negocio.
* Acceder directamente a la base de datos.

---

## Controllers

Intermediarios entre la interfaz y la lógica del negocio.

Funciones:

* Recibir eventos de la interfaz.
* Validar datos básicos.
* Invocar servicios.
* Actualizar vistas.

Ejemplo:

```text
Botón Guardar

↓
Controller

↓
Service
```

---

## Services

Implementan las reglas de negocio.

Funciones:

* Validaciones complejas.
* Generación de cuotas.
* Registro de pagos.
* Cálculo de saldos.
* Aplicación de becas.
* Gestión de matrículas.
* Control de inventario.
* Auditoría.

Todo lo definido en:

```text
reglas_negocio.md
```

debe implementarse en esta capa.

---

## Repositories

Encapsulan el acceso a la base de datos.

Funciones:

* INSERT
* UPDATE
* SELECT
* Soft Delete

No deben contener reglas de negocio.

---

## Database

Responsable de:

* Conexión SQLite.
* Creación de tablas.
* Restauración de respaldos.
* Generación de respaldos.
* Carga de datos iniciales.

---

# Estructura del Proyecto

```text
src/

├── main.py

├── database/
│   ├── connection.py
│   ├── create_db.py
│   ├── backup.py
│   ├── restore.py
│   └── seed.py

├── models/
│   ├── persona.py
│   ├── usuario.py
│   ├── apoderado.py
│   ├── estudiante.py  # + foto_path, fecha_matricula (RN-041)
│   ├── estudiante_apoderado.py
│   ├── categoria.py
│   ├── tarifa.py
│   ├── beca.py
│   ├── matricula.py
│   ├── matricula_beca.py
│   ├── cuota.py  # monto_mora (RN-020)
│   ├── pago.py  # numero_recibo UNIQUE (RN-022)
│   ├── detalle_pago.py
│   ├── categoria_producto.py
│   ├── producto.py  # precio_compra/venta, id_tipo_uniforme (RN-038/039)
│   ├── movimiento_inventario.py
│   ├── tipo_uniforme.py  # v2: Entrenamiento/Competencia/Completo/Media
│   ├── venta.py + detalle_venta.py  # v2: UNIFORME/TIENDA/CAMPEONATO/INSCRIPCION
│   ├── egreso.py  # v2: PROFESOR/PERSONAL/CAMPEONATO_FIJO/ARBITRAJE/VIATICOS
│   ├── configuracion.py  # + precio_inscripcion/mensualidad/uniforme/reingreso, tasa, arbitraje, pago_profesor, pin_emergencia
│   └── log.py

├── repositories/
│   ├── persona_repository.py
│   ├── usuario_repository.py
│   ├── estudiante_repository.py
│   ├── apoderado_repository.py
│   ├── matricula_repository.py
│   ├── cuota_repository.py
│   ├── pago_repository.py
│   ├── producto_repository.py
│   ├── configuracion_repository.py
│   └── log_repository.py

├── services/
│   ├── auth_service.py  # login + PIN emergencia hasheado
│   ├── estudiante_service.py  # foto_path + reingreso
│   ├── matricula_service.py  # diferir 2-3 cuotas + primera matrícula -1 camiseta
│   ├── cuota_service.py  # mora PORCENTAJE/MONTO_FIJO
│   ├── pago_service.py  # comprobante_path
│   ├── venta_service.py  # v2: registra venta + descuenta stock atómico
│   ├── egreso_service.py  # v2: reporte ingresos vs egresos
│   ├── tipo_uniforme_service.py
│   ├── inventario_service.py  # precio_compra/venta + tipo_uniforme
│   ├── configuracion_service.py  # 7 precios flexibles
│   ├── reporte_service.py  # 9 reportes
│   └── backup_service.py  # OneDrive central

├── controllers/
│   ├── login_controller.py
│   ├── dashboard_controller.py
│   ├── estudiante_controller.py  # foto + reingreso venta
│   ├── matricula_controller.py  # diferir
│   ├── pago_controller.py  # comprobante + cuotas pendientes wrapper
│   ├── venta_controller.py  # v2
│   ├── egreso_controller.py  # ADMIN
│   ├── tipo_uniforme_controller.py  # ADMIN
│   ├── inventario_controller.py  # tipo_uniforme
│   ├── configuracion_controller.py  # 7 precios + OneDrive
│   └── usuario_controller.py

├── views/
│   ├── login/  # cambiar_password topmost
│   ├── dashboard/  # + Ventas/Egresos/Neto/Nuevos vs Antiguos (26)
│   ├── estudiantes/  # + foto thumbnail 60
│   ├── matriculas/  # + diferir 2/3 meses
│   ├── pagos/  # + comprobante OneDrive
│   ├── ventas/  # v2: UNIFORME/TIENDA/CAMPEONATO
│   ├── egresos/  # v2: ADMIN
│   ├── inventario/  # + compra/venta/ganancia + tipo_uniforme
│   ├── configuracion/  # + 7 precios + tipos uniforme + visual (font_scale)
│   ├── usuarios/
│   └── reportes/  # + ingresos vs egresos, stock bajo uniformes, nuevos vs antiguos

├── reports/
│   ├── excel_generator.py
│   └── templates/

├── utils/
│   ├── constants.py  # OneDrive detect + DB_PATH config.ini + FOTOS_DIR/COMPROBANTES_DIR
│   ├── validators.py
│   ├── ui_helpers.py  # hover + cards
│   ├── date_utils.py / dates.py
│   ├── money_utils.py / helpers.py
│   ├── security_utils.py / security.py
│   └── logger.py

└── assets/
    ├── icons/
    └── images/
```

---

# Modelos

Las entidades de negocio se representarán mediante clases usando:

```python
@dataclass
```

Ejemplo:

```python
from dataclasses import dataclass

@dataclass
class Estudiante:
    id_estudiante: int | None
    id_persona: int
    estado: str
    fecha_ingreso: str
    fecha_retiro: str | None
    activo: int = 1
```

Beneficios:

* Mayor legibilidad.
* Tipado explícito.
* Menos errores de acceso a campos.
* Mejor soporte del IDE.

---

# Gestión de Roles

## ADMIN

Acceso total al sistema.

Puede:

* Gestionar usuarios.
* Gestionar configuraciones.
* Gestionar categorías.
* Gestionar tarifas.
* Gestionar becas.
* Consultar auditoría.
* Crear backups.
* Restaurar backups.
* Consultar todos los reportes.

---

## SECRETARIA

Operación diaria.

Puede:

* Registrar estudiantes (con foto) + apoderados (máx 2, 1 principal).
* Registrar matrículas (diferir 2-3, primera descuenta camiseta).
* Registrar pagos (YAPE con comprobante) + ventas (uniforme/tienda).
* Gestionar inventario (ver) + tipos uniforme (ver).
* Consultar dashboard (14 cards) + reportes (6 base).
* Importar no (solo ADMIN).

No puede:

* Egresos / Usuarios / Auditoría / Configuración global / Restore / Tarifas / Importar.

---

# Auditoría

Toda operación relevante deberá generar un registro en la tabla LOG.

Eventos mínimos:

* INSERT
* UPDATE
* DESACTIVACIÓN

Información almacenada:

* Usuario responsable.
* Tabla afectada.
* Registro afectado.
* Valor anterior.
* Valor nuevo.
* Fecha y hora.

La auditoría será de solo lectura.

---

# Backups

El sistema soportará:

## Manual

Ejecutado por el administrador en cualquier momento.

## Automático

Configurado desde el módulo de configuración.

Parámetros:

* Activado / Desactivado.
* Frecuencia.
* Ruta de almacenamiento.
* Cuenta de sincronización OneDrive.

---

# Reportes (9) — Excel

* Morosos, Pagos por fecha, Ingresos mensuales, Alumnos por categoría, Inventario, Becas activas
* **v2:** Ingresos vs Egresos (pagos+ventas - egresos), Stock bajo uniformes (por tipo), Nuevos vs Antiguos

---

# Principios de Desarrollo

1. No realizar consultas SQL desde las vistas.
2. No implementar reglas de negocio en los repositories.
3. Toda regla funcional debe implementarse en services.
4. Utilizar soft delete mediante el campo activo.
5. Mantener trazabilidad mediante auditoría.
6. Centralizar constantes del sistema en utils/constants.py.
7. Mantener una única conexión administrada por database/connection.py.
8. Documentar cualquier cambio estructural en los archivos de documentación antes de implementarlo.

```
```
