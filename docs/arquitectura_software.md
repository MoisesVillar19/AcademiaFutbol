# Arquitectura de Software

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
│   ├── estudiante.py
│   ├── estudiante_apoderado.py
│   ├── categoria.py
│   ├── tarifa.py
│   ├── beca.py
│   ├── matricula.py
│   ├── matricula_beca.py
│   ├── cuota.py
│   ├── pago.py
│   ├── detalle_pago.py
│   ├── categoria_producto.py
│   ├── producto.py
│   ├── movimiento_inventario.py
│   ├── configuracion.py
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
│   ├── auth_service.py
│   ├── estudiante_service.py
│   ├── matricula_service.py
│   ├── cuota_service.py
│   ├── pago_service.py
│   ├── inventario_service.py
│   ├── configuracion_service.py
│   ├── reporte_service.py
│   └── backup_service.py

├── controllers/
│   ├── login_controller.py
│   ├── dashboard_controller.py
│   ├── estudiante_controller.py
│   ├── matricula_controller.py
│   ├── pago_controller.py
│   ├── inventario_controller.py
│   ├── configuracion_controller.py
│   └── usuario_controller.py

├── views/
│   ├── login/
│   ├── dashboard/
│   ├── estudiantes/
│   ├── matriculas/
│   ├── pagos/
│   ├── inventario/
│   ├── configuracion/
│   ├── usuarios/
│   └── reportes/

├── reports/
│   ├── excel_generator.py
│   └── templates/

├── utils/
│   ├── constants.py
│   ├── validators.py
│   ├── date_utils.py
│   ├── money_utils.py
│   ├── security_utils.py
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

Operación diaria del sistema.

Puede:

* Registrar estudiantes.
* Registrar apoderados.
* Registrar matrículas.
* Registrar pagos.
* Gestionar inventario.
* Consultar dashboard.
* Generar reportes permitidos.

No puede:

* Gestionar usuarios.
* Acceder a auditoría.
* Modificar configuraciones globales.
* Restaurar backups.

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

# Reportes Iniciales

Reportes Excel disponibles:

* Morosos.
* Pagos por fecha.
* Ingresos mensuales.
* Alumnos por categoría.
* Inventario.
* Becas activas.

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
