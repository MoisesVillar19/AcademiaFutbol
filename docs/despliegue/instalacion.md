# Guía de Instalación

## Instalación con Inno Setup (Recomendado)

### Paso 1: Descargar el instalador

Descargar el archivo `AcademiaFutbol-Setup-X.X.X.exe` desde:
- OneDrive (compartido por el administrador)
- USB
- Correo electrónico

### Paso 2: Ejecutar el instalador

1. Hacer doble clic en el archivo `.exe`
2. Si Windows muestra una advertencia de seguridad, hacer clic en "Más información" → "Ejecutar de todas formas"
3. Aparecerá el wizard de instalación

### Paso 3: Configurar la instalación

1. **Bienvenida**: Hacer clic en "Siguiente"
2. **Licencia**: Aceptar los términos
3. **Carpeta de instalación**: Dejar la ruta por defecto (`C:\Program Files\AcademiaFutbol\`) o elegir otra
4. **Acceso directo**: Marcar "Crear acceso directo en el escritorio"
5. **Instalar**: Hacer clic en "Instalar"
6. **Finalizar**: Marcar "Abrir AcademiaFutbol ahora" y hacer clic en "Finalizar"

### Paso 4: Primer inicio

1. Abrir la app desde el acceso directo del escritorio
2. Iniciar sesión con:
   - Usuario: `admin`
   - Contraseña: `admin123`
3. Cambiar la contraseña inmediatamente
4. Configurar la ruta de backup en OneDrive (Configuración)

## Instalación sin Inno Setup

### Paso 1: Descargar el ejecutable

Descargar la carpeta `AcademiaFutbol` completa desde GitHub Releases o USB.

### Paso 2: Extraer

1. Crear una carpeta en `C:\AcademiaFutbol\`
2. Copiar todos los archivos de la carpeta descargada

### Paso 3: Crear acceso directo

1. Ir a `C:\AcademiaFutbol\`
2. Hacer clic derecho en `AcademiaFutbol.exe`
3. Seleccionar "Crear acceso directo"
4. Mover el acceso directo al escritorio

## Ejecutar desde código fuente (Desarrolladores)

### Requisitos

- Python 3.13 o superior
- pip

### Pasos

```bash
# Clonar el repositorio
git clone https://github.com/MoisesVillar19/AcademiaFutbol.git
cd AcademiaFutbol

# Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la app
python main.py
```

## Construir el ejecutable (Desarrolladores)

```bash
# Instalar PyInstaller
pip install pyinstaller

# Ejecutar script de construcción
build.bat
```

El ejecutable se generará en `dist\AcademiaFutbol\`

## Construir el instalador (Desarrolladores)

### Requisitos

- Inno Setup 6.7+ instalado
- Ejecutable ya construido con PyInstaller

### Pasos

```bash
cd installer
build_installer.bat
```

El instalador se generará en `installer\Output\`

## Configuración de OneDrive

### Si OneDrive está instalado

La app detecta OneDrive automáticamente y guarda backups en:
```
C:\Users\{usuario}\OneDrive\BackupsAcademia\
```

Para configurar:
1. Abrir la app
2. Ir a Configuración
3. Verificar la ruta de backup
4. Cambiar si es necesario

### Si OneDrive NO está instalado

Los backups se guardan localmente en:
```
C:\Program Files\AcademiaFutbol\backups\
```

**Recomendación:** Instalar OneDrive para sincronización automática en la nube.

## Desinstalar

### Con Inno Setup

1. Ir a Panel de Control → Programas y características
2. Buscar "AcademiaFutbol"
3. Hacer clic en "Desinstalar"
4. Seguir el wizard

### Sin Inno Setup

1. Eliminar la carpeta `C:\AcademiaFutbol\`
2. Eliminar el acceso directo del escritorio
3. (Opcional) Eliminar la BD en `OneDrive\BackupsAcademia\` si no se necesita
