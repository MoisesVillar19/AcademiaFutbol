# Sprint 10 — Estabilización

**Fecha:** 2026-08-01
**Objetivo:** Preparar versión 1.0 estable

---

## Prioridad 1 — Bugs Críticos

### Bug #7: `id_usuario=1` hardcodeado (17 ocurrencias)

**Problema:** Todos los services usan `id_usuario=1` en llamadas a auditoría.

**Solución:** Modificar cada función para aceptar `id_usuario` como parámetro.

**Archivos a modificar:**

| Archivo | Líneas | Funciones |
|---------|--------|-----------|
| `services/usuario_service.py` | 48, 93, 123, 150, 170 | `crear_usuario`, `editar_usuario`, `activar_usuario`, `desactivar_usuario`, `restablecer_password` |
| `services/persona_service.py` | 36, 70 | `crear_persona`, `editar_persona` |
| `services/estudiante_service.py` | 47, 96, 118 | `crear_estudiante`, `registrar_retiro`, `registrar_reingreso` |
| `services/apoderado_service.py` | 48, 92 | `crear_apoderado`, `asociar_a_estudiante` |
| `services/matricula_service.py` | 74 | `crear_matricula` |
| `services/tarifa_service.py` | 31 | `crear_tarifa` |
| `services/beca_service.py` | 31 | `crear_beca` |
| `services/inventario_service.py` | 23, 95, 185 | `registrar_producto`, `registrar_movimiento`, `registrar_ajuste` |

**Patrón de cambio:**

```python
# ANTES
def crear_estudiante(data: dict) -> tuple[bool, str, int | None]:
    ...
    auditoria_service.registrar_insert(id_usuario=1, ...)

# DESPUÉS
def crear_estudiante(data: dict, id_usuario: int) -> tuple[bool, str, int | None]:
    ...
    auditoria_service.registrar_insert(id_usuario=id_usuario, ...)
```

**Controllers a modificar:**

Cada controller debe obtener `id_usuario` de `auth_service.obtener_usuario_actual()` y pasarlo al service.

```python
# En cada controller
from services import auth_service

def crear_estudiante(data: dict):
    usuario = auth_service.obtener_usuario_actual()
    id_usuario = usuario["id_usuario"] if usuario else 1
    return estudiante_service.crear_estudiante(data, id_usuario)
```

---

### Bug #18: SHA-256 débil → bcrypt

**Problema:** `utils/security.py` usa `hashlib.sha256` que es inseguro para passwords.

**Solución:** Migrar a `bcrypt` (ya instalado).

**Archivo a modificar:** `utils/security.py`

**Cambios:**

```python
# ANTES
import hashlib
import os

def hash_password(password: str) -> str:
    salt = os.urandom(32)
    hash_obj = hashlib.sha256(salt + password.encode())
    return (salt + hash_obj.digest()).hex()

def verify_password(password: str, stored_hash: str) -> bool:
    # Comparación incorrecta por salt aleatorio

# DESPUÉS
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, stored_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), stored_hash.encode())
```

**Nota:** Se debe recrear el seed con passwords hasheados con bcrypt.

---

### Bug #12: Filtro "Retirados" erróneo

**Problema:** `estudiante_view.py:284-285` filtra por `activo=0` en vez de `estado='RETIRADO'`.

**Archivo:** `views/estudiantes/estudiante_view.py`

**Cambio:**

```python
# ANTES
elif valor == "Retirados":
    self._cargar_estudiantes(activo=0)

# DESPUÉS
elif valor == "Retirados":
    self._cargar_estudiantes(estado="RETIRADO")
```

**Requiere:** Agregar parámetro `estado` a `_cargar_estudiantes()` y modificar `listar_estudiantes()` en el service.

---

## Prioridad 2 — Violaciones de Arquitectura

### Bug #8-9: View → Repository/Service en `pago_view.py`

**Archivo:** `views/pagos/pago_view.py`

**Cambios en `pago_controller.py`:**

```python
# Agregar funciones
def listar_matriculas_activas():
    from services import matricula_service
    return matricula_service.listar_matriculas_activas()

def listar_cuotas_pendientes(id_matricula: int):
    from services import cuota_service
    return cuota_service.obtener_cuotas_pendientes(id_matricula)
```

**Cambios en `pago_view.py`:**

```python
# ANTES
from repositories import matricula_repository
matriculas = matricula_repository.obtener_activas()

# DESPUÉS
from controllers import pago_controller
matriculas = pago_controller.listar_matriculas_activas()
```

---

### Bug #10: View → Repository en `estudiante_view.py`

**Archivo:** `views/estudiantes/estudiante_view.py:379`

**Cambios en `estudiante_controller.py`:**

```python
# Agregar función
def obtener_apoderado_por_persona(id_persona: int):
    from repositories import apoderado_repository
    return apoderado_repository.obtener_por_persona(id_persona)
```

---

### Bug #16: Service → Database en `dashboard_service.py`

**Archivo:** `services/dashboard_service.py:115`

**Cambio:**

```python
# ANTES
def _obtener_configuracion():
    from database.connection import fetch_one
    return fetch_one("SELECT * FROM configuracion WHERE id_configuracion = 1")

# DESPUÉS
def _obtener_configuracion():
    from repositories import configuracion_repository
    return configuracion_repository.obtener_configuracion()
```

---

## Prioridad 3 — Limpieza de Código

| Acción | Archivo | Línea |
|--------|---------|-------|
| Eliminar código muerto | `matricula_service.py` | 39 |
| Eliminar import redundante | `matricula_service.py` | 69 |
| Eliminar función muerta | `database/connection.py` | 27-32 |
| Eliminar import muerto | `repositories/estudiante_apoderado_repository.py` | 2 |
| Agregar `__init__.py` | `views/dashboard/`, `views/estudiantes/`, `views/inventario/`, `views/matriculas/`, `views/pagos/`, `views/reportes/` |
| Usar constantes | Múltiples archivos | `METODO_EFECTIVO`, `METODO_YAPE`, etc. |

---

## Prioridad 4 — Tests

### Configuración

1. Instalar pytest: `pip install pytest`
2. Agregar `pytest` a `requirements.txt`
3. Crear `tests/conftest.py` con fixtures

### `tests/conftest.py`

```python
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database.create_db import create_tables
from database.seed import seed_database

@pytest.fixture(autouse=True)
def setup_database():
    create_tables()
    seed_database()
    yield
    # Cleanup

@pytest.fixture
def usuario_admin():
    from services import auth_service
    auth_service.login("admin", "admin123")
    yield
    auth_service.logout()
```

### Tests a crear

| Archivo | Cobertura |
|---------|-----------|
| `tests/test_validators.py` | `validate_dni`, `validate_not_empty`, `validate_sex`, `validate_email`, `validate_phone` |
| `tests/test_security.py` | `hash_password`, `verify_password`, `generate_temp_password`, `generate_receipt_number` |
| `tests/test_dates.py` | `get_today`, `get_now`, `format_date` |
| `tests/test_cuota_service.py` | `crear_cuota`, `actualizar_pago`, `actualizar_estados_vencidos` |
| `tests/test_pago_service.py` | `registrar_pago`, `obtener_pago` |
| `tests/test_estudiante_service.py` | `crear_estudiante`, `editar_estudiante`, `registrar_retiro`, `registrar_reingreso` |
| `tests/test_login.py` | Login exitoso, login fallido, logout, sesión |
| `tests/test_matriculas.py` | `crear_matricula`, `asociar_beca` |

---

## Prioridad 5 — Documentación

### `README.md` — Reescritura completa

```markdown
# AcademiaFutbol

Sistema de Gestión para Academia Deportiva.

## Tecnologías
- Python 3.x
- SQLite
- CustomTkinter
- openpyxl
- matplotlib

## Instalación
```bash
pip install -r requirements.txt
```

## Ejecución
```bash
python main.py
```

## Credenciales por defecto
- Usuario: `admin`
- Contraseña: `admin123`

## Arquitectura
- Views → Controllers → Services → Repositories → SQLite

## Estructura del proyecto
...
```

### Renombrar `sprint7_estado.md` → `estado_actual.md`

### Actualizar `AGENTS.md`

Corregir referencia de `arquitectura_bd.md` a `AcademiaFutbol_Arquitectura_BD.md`.

---

## Prioridad 6 — Seguridad y Config

### `.env`

```
DB_NAME=academia.db
DEFAULT_ADMIN_USER=admin
DEFAULT_ADMIN_PASS=admin123
BACKUP_DIR=backups/
```

### `utils/constants.py`

```python
import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv("DB_NAME", "academia.db")
DEFAULT_ADMIN_USER = os.getenv("DEFAULT_ADMIN_USER", "admin")
DEFAULT_ADMIN_PASS = os.getenv("DEFAULT_ADMIN_PASS", "admin123")
```

---

## Prioridad 7 — Git

1. **Commit de Sprints 1-9:**
```bash
git add .
git commit -m "feat: Sprints 1-9 completados

- Sprint 1: Database (SQLite, models, seed, backup)
- Sprint 2: Security (auth, usuarios, auditoría)
- Sprint 3: Académica (personas, apoderados, estudiantes)
- Sprint 4: Matrículas (tarifas, becas, cuotas)
- Sprint 5: Pagos (registro, detalle)
- Sprint 6: Inventario (productos, movimientos)
- Sprint 7: Dashboard interactivo con gráficos
- Sprint 8: Reportes exportables a Excel
- Sprint 9: Configuración del sistema"
```

2. **Commit de Sprint 10:**
```bash
git add .
git commit -m "feat: Sprint 10 - Estabilización

- Fix bugs críticos (#7, #12, #18)
- Corregir violaciones de arquitectura
- Agregar tests unitarios y de integración
- Actualizar documentación
- Migrar a bcrypt para passwords
- Implementar variables de entorno"
```

3. **Tag v1.0:**
```bash
git tag -a v1.0 -m "Versión 1.0 estable"
```

---

## Checklist de Verificación

- [ ] Bug #7 corregido (id_usuario dinámico)
- [ ] Bug #18 corregido (bcrypt)
- [ ] Bug #12 corregido (filtro retirados)
- [ ] Bugs #8-10 corregidos (violaciones arquitectura)
- [ ] Bug #16 corregido (dashboard_service)
- [ ] Código muerto eliminado
- [ ] `__init__.py` agregados
- [ ] pytest instalado
- [ ] conftest.py creado
- [ ] Tests unitarios escritos
- [ ] Tests de integración escritos
- [ ] README.md actualizado
- [ ] Documentación actualizada
- [ ] `.env` implementado
- [ ] Git commit realizado
- [ ] Tag v1.0 creado

---

## Prioridad 8 — Extras (Opcional)

| # | Item | Descripción |
|---|------|-------------|
| 1 | Agregar `reports/` a `.gitignore` | Si solo se usa `exports/` |
| 2 | Mejorar error handling en `main.py` | Usar `messagebox.showerror()` en vez de `print()` para errores críticos |
| 3 | Logging en backup/restore | Registrar operaciones de backup/restore en tabla `log` |
| 4 | Validación en restore | Verificar integridad del archivo SQLite antes de restaurar |
