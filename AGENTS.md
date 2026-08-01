# AGENTS.md

# Proyecto

Sistema de Gestión para Academia Deportiva.

Tecnologías principales:

* Python 3.x
* SQLite
* CustomTkinter
* openpyxl
* Git

---

# Objetivo del Sistema

Administrar:

* Estudiantes
* Apoderados
* Matrículas
* Cuotas
* Pagos
* Inventario
* Reportes
* Configuración
* Auditoría

El sistema está orientado a una academia deportiva.

---

# Documentación del Proyecto

Antes de modificar cualquier componente, revisar:

```text
docs/

arquitectura_bd.md
diccionario_datos.md
reglas_negocio.md
casos_de_uso.md
arquitectura_software.md
convenciones_codigo.md
roadmap.md
plan_sprints.md
```

Las decisiones definidas en esos documentos tienen prioridad sobre cualquier sugerencia automática.

---

# Arquitectura

La aplicación utiliza arquitectura por capas.

```text
View
 ↓
Controller
 ↓
Service
 ↓
Repository
 ↓
SQLite
```

---

# Responsabilidades

## Views

Responsables únicamente de:

* Mostrar información.
* Capturar acciones del usuario.

No deben:

* Ejecutar SQL.
* Aplicar reglas de negocio.
* Acceder directamente a SQLite.

---

## Controllers

Responsables de:

* Recibir eventos de la interfaz.
* Invocar Services.
* Coordinar la actualización de Views.

---

## Services

Contienen toda la lógica del negocio.

Ejemplos:

* Registrar pagos.
* Generar cuotas.
* Calcular saldos.
* Aplicar becas.
* Gestionar matrículas.

Toda regla definida en:

```text
docs/reglas_negocio.md
```

debe implementarse aquí.

---

## Repositories

Responsables únicamente del acceso a datos.

Permitido:

* INSERT
* UPDATE
* SELECT

No permitido:

* Reglas de negocio.
* Cálculos financieros.
* Validaciones complejas.

---

## Database

Responsable de:

* connection.py
* create_db.py
* seed.py
* backup.py
* restore.py

---

# Base de Datos

Motor:

```text
SQLite
```

Toda la estructura está definida en:

```text
docs/arquitectura_bd.md
docs/diccionario_datos.md
```

No crear tablas fuera de:

```python
database/create_db.py
```

---

# Soft Delete

No eliminar registros físicamente.

Utilizar:

```python
activo = 0
```

Evitar:

```sql
DELETE FROM
```

salvo mantenimiento interno controlado.

---

# Modelos

Todos los modelos deben implementarse usando:

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
    activo: int = 1
```

---

# Convenciones de Código

## Archivos

```text
snake_case.py
```

Ejemplos:

```text
pago_service.py
matricula_repository.py
login_controller.py
```

---

## Clases

```python
PascalCase
```

Ejemplo:

```python
class PagoService:
    pass
```

---

## Funciones

```python
snake_case
```

Ejemplo:

```python
def registrar_pago():
    pass
```

---

## Constantes

```python
UPPER_CASE
```

Ejemplo:

```python
ROLE_ADMIN
ROLE_SECRETARIA
```

---

# Roles del Sistema

## ADMIN

Acceso total.

Puede:

* Gestionar usuarios.
* Gestionar configuración.
* Consultar auditoría.
* Crear backups.
* Restaurar backups.
* Gestionar categorías.
* Gestionar tarifas.
* Gestionar becas.

---

## SECRETARIA

Puede:

* Gestionar estudiantes.
* Gestionar apoderados.
* Gestionar matrículas.
* Gestionar pagos.
* Gestionar inventario.
* Consultar dashboard.
* Generar reportes.

No puede:

* Gestionar usuarios.
* Consultar auditoría.
* Modificar configuraciones globales.
* Restaurar backups.

---

# Reglas Importantes del Negocio

## Matrículas

Un estudiante puede tener múltiples matrículas a lo largo del tiempo.

Cuando exista reingreso:

* No reactivar matrícula anterior.
* Crear nueva matrícula.

---

## Cuotas

Las cuotas son:

```text
Mensuales
```

Estados permitidos:

```text
PENDIENTE
PARCIAL
PAGADO
VENCIDO
```

---

## Pagos

Se permiten:

* Pagos completos.
* Pagos parciales.

Una cuota puede tener múltiples pagos.

---

## Apoderados

Un estudiante:

* Debe tener un apoderado principal.
* Puede tener apoderados secundarios.

---

## Inventario

Categorías iniciales:

```text
INSUMO_DEPORTIVO
INSUMO_ALIMENTO
```

Tipos de uso:

```text
CONSUMO_INTERNO
VENTA
```

---

# Auditoría

Toda operación relevante debe registrarse en LOG.

Eventos mínimos:

* INSERT
* UPDATE
* DESACTIVACIÓN

La auditoría es:

```text
Solo lectura
```

Incluso para ADMIN.

---

# Configuración

Los siguientes parámetros deben obtenerse desde la tabla CONFIGURACION:

* mora_habilitada
* porcentaje_mora
* dias_por_vencer
* permitir_multiples_becas
* backup_automatico
* frecuencia_backup
* ruta_backup
* correo_onedrive

No hardcodear estos valores.

---

# Seguridad

Nunca almacenar contraseñas en texto plano.

Utilizar hash seguro.

---

# SQL

Preferencias:

* Consultas parametrizadas.
* Evitar concatenación de strings.
* Manejo adecuado de transacciones.

Ejemplo:

```python
cursor.execute(
    "SELECT * FROM persona WHERE dni = ?",
    (dni,)
)
```

---

# Logging

Registrar errores relevantes.

Nunca ocultar excepciones silenciosamente.

Evitar:

```python
except:
    pass
```

Preferir:

```python
except Exception as e:
    logger.error(str(e))
    raise
```

---

# Antes de Generar Código

Verificar:

1. Que respete la arquitectura por capas.
2. Que respete las reglas de negocio.
3. Que respete las convenciones del proyecto.
4. Que no duplique lógica existente.
5. Que no introduzca SQL en Views.
6. Que no introduzca reglas de negocio en Repositories.
7. Que mantenga compatibilidad con SQLite.

---

# Prioridad de Decisiones

Si existe conflicto entre instrucciones:

```text
1. AGENTS.md
2. docs/reglas_negocio.md
3. docs/arquitectura_bd.md
4. docs/diccionario_datos.md
5. docs/arquitectura_software.md
6. docs/convenciones_codigo.md
```

La documentación del proyecto tiene prioridad sobre las sugerencias automáticas del agente.
