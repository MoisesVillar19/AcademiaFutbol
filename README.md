# AcademiaFutbol

Sistema de gestión para academia deportiva. Administra estudiantes, matrículas, pagos, inventario y reportes.

## Requisitos

- Windows 10/11
- 4 GB de RAM mínimo
- 500 MB de espacio en disco
- Conexión a internet (para actualizaciones y backups a OneDrive)

## Instalación

### Opción 1: Instalador (Recomendado)

1. Descargar `AcademiaFutbol-Setup-X.X.X.exe`
2. Ejecutar el archivo descargado
3. Seguir el wizard de instalación
4. Marcar "Crear acceso directo en el escritorio"
5. Hacer clic en "Instalar"
6. Abrir desde el acceso directo en el escritorio

### Opción 2: Ejecutable directo

1. Descargar y extraer la carpeta `AcademiaFutbol`
2. Ejecutar `AcademiaFutbol.exe`
3. (Opcional) Crear acceso directo en el escritorio

## Credenciales por defecto

| Campo | Valor |
|-------|-------|
| Usuario | `admin` |
| Contraseña | `admin123` |

**IMPORTANTE:** Cambiar la contraseña después del primer inicio de sesión.

## Actualizaciones

La aplicación verifica actualizaciones automáticamente al iniciar (una vez al día).

Cuando haya una nueva versión:
1. Aparecerá un diálogo "Nueva versión disponible"
2. Hacer clic en "Actualizar"
3. La app se descargará y reiniciará automáticamente

Para verificar manualmente: reiniciar la aplicación.

## Estructura del proyecto

```
AcademiaFutbol/
├── main.py                    # Punto de entrada
├── VERSION                    # Versión actual
├── models/                    # Modelos de datos
├── repositories/              # Acceso a datos
├── services/                  # Lógica del negocio
├── controllers/               # Controladores
├── views/                     # Interfaz gráfica
├── utils/                     # Utilidades
├── database/                  # Base de datos SQLite
├── updater/                   # Sistema de actualización
├── assets/                    # Iconos e imágenes
├── installer/                 # Scripts de instalador
└── docs/                      # Documentación
```

## Solución de problemas

### La app no abre
- Verificar que Python 3.13+ esté instalado (si ejecuta desde código fuente)
- Ejecutar `pip install -r requirements.txt`
- Verificar que no haya otra instancia de la app abierta

### Error de base de datos
- La app crea la BD automáticamente al primer inicio
- No modificar manualmente los archivos `.db`
- Si hay problemas, eliminar `database/academia.db` y reiniciar (se perderán los datos)

### Backup no se sincroniza
- Verificar que OneDrive esté instalado y configurado
- La app guarda backups en `OneDrive\BackupsAcademia\`
- Si no tiene OneDrive, los backups se guardan en `backups/` local

### Actualización falla
- Verificar conexión a internet
- Si persiste, descargar manualmente desde GitHub Releases
- El repo debe ser público para que las actualizaciones funcionen

## Tecnologías

- Python 3.13
- SQLite
- CustomTkinter
- OpenPyXL
- ReportLab

## Licencia

Proyecto privado - Academia Deportiva
