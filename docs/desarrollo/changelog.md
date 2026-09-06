# Changelog - Correccion de Bugs y Sincronizacion de BD

**Fecha:** 2026-08-07
**Commits:** c935bf0, 1118793, f06204c

---

## Problemas Detectados y Corregidos

### 1. Sincronizacion del Schema de Base de Datos

La BD real tenia un schema diferente al definido en `create_db.py`, causando errores al guardar registros.

| Tabla | Problema | Solucion |
|-------|----------|----------|
| `persona` | `CHECK(sexo IN ('M','F'))` rechazaba strings vacios | Recreada sin CHECK constraint |
| `apoderado` | Faltaban columnas `tipo_documento`, `telefono`, `direccion` | Columnas agregadas via ALTER TABLE |
| `persona` | Faltaba columna `tipo_documento` | Columna agregada via ALTER TABLE |
| `tarifa` | Tenia `fecha_inicio NOT NULL` y `fecha_fin` innecesarias | Columnas eliminadas (solo monto importa) |

### 2. Botones de Guardar No Funcionaban

#### 2.1 Estudiante + Apoderado (estudiante_view.py)
- **Bug:** `from controllers import apoderado_controller` importaba un modulo inexistente
- **Solucion:** Cambiado a `estudiante_controller.crear_apoderado()` que es donde esta la funcion

#### 2.2 Tarifa (tarifa_service.py, tarifa_repository.py)
- **Bug:** Constructor `Tarifa(fecha_inicio=..., fecha_fin=...)` pasaba campos inexistentes en el modelo
- **Bug:** SQL `ORDER BY t.fecha_inicio DESC` referenciaba columna inexistente
- **Solucion:** Eliminados `fecha_inicio`/`fecha_fin` del modelo, service y repository

#### 2.3 Inventario (inventario_view.py, inventario_controller.py)
- **Bug:** `self.entry_codigo.delete(0, "end")` referenciaba un widget inexistente (solo existe `self.label_codigo`)
- **Bug:** `crear_producto` validaba `data.get("codigo")` pero la vista nunca envia ese campo
- **Solucion:** Eliminada referencia a `entry_codigo` y validacion de codigo en controller

#### 2.4 Pagos (pago_view.py)
- **Bug:** `combo_estudiante` no tenia `command=` para cargar cuotas al seleccionar estudiante
- **Solucion:** Agregado callback `_on_estudiante_cambiado` que invoca `_cargar_combo_cuotas`

#### 2.5 Usuarios (usuario_view.py, usuario_controller.py)
- **Bug:** 3 CTkInputDialog separados (username, DNI, rol) - UX confusa
- **Bug:** `editar_usuario` se llamaba con argumentos posicionales incorrectos `(id, username, rol)` en vez de `(id, data)`
- **Solucion:** Nuevo `CrearUsuarioDialog` centrado con un solo formulario. Firma corregida a `(id, data)`

### 3. Campos No Persistidos

| Archivo | Campos faltantes |
|---------|-----------------|
| `apoderado_service.py` | `telefono` y `direccion` no se pasaban al crear apoderado |
| `configuracion_service.py` | `tipo_mora` y `monto_mora` no se pasaban al actualizar configuracion |
| `usuario_service.py` | No se manejaba cambio de password en `editar_usuario` |

### 4. Error Visual

#### Ventana de Cambio de Contrasena (cambiar_password_view.py)
- **Bug:** `self.geometry("440x460")` se ejecutaba sin posicion, luego `_centrar_ventana()` usaba tamaño diferente (420x420). El `-topmost` parpadeaba y la ventana se perdia atras
- **Solucion:** Eliminado `self.geometry()` inicial. `_centrar_ventana()` calcula posicion centrada con tamaño correcto. Solo `lift()` + `focus_force()` sin `-topmost`

### 5. Imports Rotos

| Archivo | Import incorrecto | Solucion |
|---------|-------------------|----------|
| `database/backup.py` | `from database.connection import DB_PATH` | Cambiado a `from utils.constants import DB_PATH` |
| `database/restore.py` | `from database.connection import DB_PATH` | Cambiado a `from utils.constants import DB_PATH` |

### 6. Diccionarios No Inicializados

Los siguientes diccionarios de mapeo no se inicializaban en `__init__`, causando errores al acceder a ellos antes de cargar los combos:

- `EstudianteView._estudiantes_map`
- `PagoView._matriculas_map`, `_cuotas_map`
- `MatriculaView._estudiantes_map`, `_tarifas_map`, `_becas_map`, `_matriculas_map`
- `InventarioView._categorias_map`, `_productos_map`
- `TarifaView._cats_map`

**Solucion:** Todos inicializados como `{}` en `__init__`.

### 7. Importar (importar_service.py)
- **Bug:** Mapeo de columnas generaba `dni_apoderado` pero `crear_apoderado` espera `dni`
- **Solucion:** Renombradas llaves del diccionario antes de pasar al servicio

---

## Archivos Modificados

```
controllers/inventario_controller.py
database/backup.py
database/create_db.py
database/restore.py
models/tarifa.py
repositories/tarifa_repository.py
services/apoderado_service.py
services/configuracion_service.py
services/importar_service.py
services/tarifa_service.py
services/usuario_service.py
views/estudiantes/estudiante_view.py
views/inventario/inventario_view.py
views/login/cambiar_password_view.py
views/matriculas/matricula_view.py
views/pagos/pago_view.py
views/tarifas/tarifa_view.py
views/usuarios/usuario_view.py
```
