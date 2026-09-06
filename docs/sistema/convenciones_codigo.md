# Convenciones de Código

> **v2 (2026-09):** Se mantiene `snake_case` archivos, `PascalCase` clases, `UPPER_CASE` constantes. Nuevos: `utils/ui_helpers.py` helpers hover, `venta/egreso/tipo_uniforme` sigue `snake_case`, `OneDrive` paths en `utils/constants.py` via `config.ini`.

## Objetivo

Definir estándares de desarrollo para mantener consistencia, legibilidad y facilidad de mantenimiento en todo el proyecto.

Estas convenciones deberán aplicarse a todos los módulos del sistema.

---

# Estructura General

El proyecto seguirá la arquitectura definida en:

```text
arquitectura_software.md
```

Toda funcionalidad deberá respetar la separación de responsabilidades entre:

* Views
* Controllers
* Services
* Repositories
* Database

---

# Convenciones de Nombres

## Archivos

Todos los archivos utilizarán:

```text
snake_case.py
```

Ejemplos:

```text
student_service.py
payment_repository.py
backup_service.py
login_controller.py
```

No utilizar:

```text
StudentService.py
PaymentRepository.py
```

---

## Carpetas

Utilizar:

```text
snake_case
```

Ejemplos:

```text
views/
reports/
database/
```

---

## Clases

Utilizar:

```text
PascalCase
```

Ejemplos:

```python
class StudentService:
    pass

class PaymentRepository:
    pass

class LoginController:
    pass
```

---

## Funciones y Métodos

Utilizar:

```text
snake_case
```

Ejemplos:

```python
def get_student_by_id():
    pass

def register_payment():
    pass

def generate_monthly_fee():
    pass
```

---

## Variables

Utilizar:

```text
snake_case
```

Ejemplos:

```python
student_id
payment_amount
due_date
```

---

## Constantes

Utilizar:

```text
UPPER_CASE
```

Ejemplos:

```python
ROLE_ADMIN = "ADMIN"

ROLE_SECRETARIA = "SECRETARIA"

STATUS_ACTIVE = "ACTIVO"
```

---

# Organización de Imports

Orden recomendado:

## Librerías estándar

```python
import os
import sqlite3
from datetime import datetime
```

## Librerías externas

```python
import customtkinter as ctk
```

## Módulos internos

```python
from services.student_service import StudentService
```

---

# Tipado

Siempre que sea posible utilizar type hints.

Ejemplo:

```python
def get_student_by_id(
    student_id: int
) -> Student | None:
    pass
```

---

# Modelos

Todos los modelos deberán implementarse utilizando:

```python
@dataclass
```

Ejemplo:

```python
from dataclasses import dataclass

@dataclass
class Student:
    id_student: int | None
    name: str
    active: int = 1
```

---

# Repositories

Responsabilidad exclusiva:

```text
Acceso a datos
```

Permitido:

```python
create()
update()
get_by_id()
get_all()
deactivate()
```

No permitido:

```python
Calcular saldos

Aplicar becas

Validar matrículas
```

Las reglas de negocio pertenecen a Services.

---

# Services

Responsabilidad exclusiva:

```text
Reglas de negocio
```

Ejemplos:

```python
register_payment()

generate_fee()

calculate_balance()

apply_scholarship()
```

No deben contener código de interfaz gráfica.

---

# Controllers

Responsabilidad exclusiva:

```text
Coordinar Views y Services
```

Los controllers:

* Reciben eventos.
* Validan entradas básicas.
* Invocan servicios.
* Actualizan vistas.

---

# Views

Las vistas:

* Muestran información.
* Capturan acciones del usuario.

No deben:

* Ejecutar SQL.
* Aplicar reglas de negocio.
* Acceder directamente a la base de datos.

---

# SQLite

Todas las consultas deberán ejecutarse mediante Repositories.

No se permite:

```python
cursor.execute(...)
```

desde:

```text
views/
services/
controllers/
```

---

# Soft Delete

No se eliminarán registros físicamente.

Se utilizará:

```python
activo = 0
```

Ejemplo:

```python
def deactivate_student():
    pass
```

No utilizar:

```python
DELETE FROM estudiante
```

salvo procesos internos excepcionales.

---

# Manejo de Errores

Siempre utilizar:

```python
try:
    ...
except Exception as e:
    ...
```

Registrar errores relevantes en logs.

Ejemplo:

```python
try:
    repository.create(student)
except Exception as e:
    logger.error(str(e))
```

---

# Comentarios

Comentar únicamente cuando la lógica no sea evidente.

Evitar:

```python
# sumar 1
contador += 1
```

Preferir:

```python
# Se genera una nueva cuota cuando el alumno
# mantiene una matrícula activa.
```

---

# Docstrings

Funciones públicas deberán incluir docstrings.

Ejemplo:

```python
def register_payment(
    payment: Payment
) -> bool:
    """
    Registra un pago y actualiza
    el saldo de la cuota asociada.
    """
```

---

# Formato de Código

Estándar:

```text
PEP 8
```

Configuración recomendada:

```text
Black
```

Longitud máxima:

```text
88 caracteres
```

---

# Gestión de Base de Datos

Todas las tablas deberán crearse desde:

```text
database/create_db.py
```

No se crearán tablas manualmente.

---

# Auditoría

Toda operación importante deberá registrarse en:

```text
LOG
```

Ejemplos:

* Crear estudiante.
* Modificar matrícula.
* Registrar pago.
* Modificar configuración.

---

# Seguridad

Nunca almacenar contraseñas en texto plano.

Siempre utilizar:

```python
hashlib
```

o una librería especializada.

La contraseña almacenada deberá corresponder a un hash.

---

# Git

## Rama Principal

```text
main
```

---

## Desarrollo

Cada funcionalidad deberá desarrollarse en una rama propia.

Ejemplos:

```text
feature/login

feature/students

feature/payments

feature/inventory
```

---

## Commits

Formato recomendado:

```text
tipo: descripción
```

Ejemplos:

```text
feat: agregar registro de pagos

fix: corregir cálculo de saldo

docs: actualizar reglas de negocio

refactor: reorganizar repositories
```

---

# Principios Generales

1. Mantener código simple y legible.
2. Evitar duplicación de lógica.
3. Respetar la arquitectura por capas.
4. Centralizar constantes reutilizables.
5. Priorizar mantenibilidad sobre optimización prematura.
6. Documentar cambios importantes.
7. Escribir código pensando en futuras ampliaciones del sistema.
