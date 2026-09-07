# Guía de Instalación — AcademiaFutbol v1.0.0

> **Versión:** 1.0.0 · **Fecha:** 2026-09-06 · **BD Central:** `OneDrive\Academia\academia.db` (virgen producción) · **Instalador:** `AcademiaFutbol-Setup-1.0.0.exe` (42 MB) · **Relacionado:** `despliegue_produccion.md`, `manual_sistema.md`, `AcademiaFutbol.spec`

---

## Resumen despliegue actual

- **Build generado:** 2026-09-06 21:02 con `build.bat` → `dist/AcademiaFutbol/AcademiaFutbol.exe` (17.5 MB, 1922 archivos) — **no contiene BD** (`AcademiaFutbol.spec:18` excluye `academia.db` y `config.ini`)
- **Instalador:** `installer/Output/AcademiaFutbol-Setup-1.0.0.exe` (42.1 MB) via Inno Setup 6.7 — `setup.iss:82` `CurStepChanged` genera `config.ini` y estructura OneDrive solo si no existe (no sobreescribe en updates)
- **BD central producción:** `C:\Users\{usuario}\OneDrive\Academia\academia.db` **virgen** (294 KB) — `create_db:370` + `seed:13` → 0 alumnos, 1 usuario `admin`, 5 categorías edad, 2 `categoria_producto`, 1 `CAMISETA-ENT` stock 50, 4 `tipo_uniforme`, precios `100/100/100/20`. BD de prueba respaldada en `OneDrive\BackupsAcademia\academia_TEST_20260906_210703.db` + `fotos_TEST_*` / `comprobantes_TEST_*`
- **Carpetas OneDrive:** `Academia\fotos\` y `Academia\comprobantes\` vacías (listas para fotos `FOTOS_DIR` y comprobantes `COMPROBANTES_DIR` `utils/constants.py:95`), `BackupsAcademia\` para backups cada 6h `main.py:242`
- **Tests:** 234 passed `pytest`

---

## 1. Instalación con Inno Setup (Recomendado) — 6 pasos deja funcional

### Requisitos previos
- Windows 10+ · OneDrive instalado y sincronizado con cuenta empresa (ej `admin@roncalli.onmicrosoft.com` con carpeta `Academia` compartida `lectura/escritura` a SECRETARIA)
- Si OneDrive no está: el wizard avisa `Instalar OneDrive recomendado` y usa fallback local `APP_DIR\database\academia.db` (no central)

### Paso 1: Descargar el instalador
**No se commitea al repo** (`.gitignore:17` `*.zip` y `installer/Output/` ignorados). Descargar desde **GitHub Releases** (ver §5) o recibir por OneDrive/USB:

- `AcademiaFutbol-Setup-1.0.0.exe` (42 MB) — instalador wizard
- Opcional: `AcademiaFutbol-v1.0.0.zip` (56 MB) — `dist\` portable sin wizard

### Paso 2: Ejecutar el instalador
1. Doble clic en `AcademiaFutbol-Setup-1.0.0.exe`
2. Si SmartScreen: `Más información → Ejecutar de todas formas` (exe sin firma)
3. Aparece wizard `AcademiaFutbol v1.0.0`

### Paso 3: Wizard (6 pantallas)
1. **Bienvenida** → `Siguiente`
2. **Licencia** → Aceptar → `Siguiente`
3. **Carpeta** → default `C:\Program Files\AcademiaFutbol\` (editable) → `Siguiente`
4. **(Automático, sin pantalla extra)** — `setup.iss:92` detecta OneDrive vía `GetEnv('OneDrive')` → crea si no existen:
   ```
   OneDrive\Academia\academia.db          (si no existe, se crea vacía al primer arranque)
   OneDrive\Academia\fotos\
   OneDrive\Academia\comprobantes\
   OneDrive\BackupsAcademia\
   ```
   Escribe `C:\Program Files\AcademiaFutbol\config.ini`:
   ```ini
   [database]
   path=C:\Users\{user}\OneDrive\Academia\academia.db
   [backup]
   dir=C:\Users\{user}\OneDrive\BackupsAcademia
   [rutas]
   # fotos/comprobantes resuelven a OneDrive\Academia\fotos si no hay clave explícita
   ```
   Si `config.ini` ya existe (update), **no se sobreescribe**.
5. **Acceso directo** → marcar `Crear acceso directo en el escritorio` → `Siguiente`
6. **Instalar** → copiar `dist\AcademiaFutbol\*` (recursivo) → `Finalizar` → marcar `Abrir AcademiaFutbol ahora`

### Paso 4: Verificación deja funcional (checklist)
- [ ] `C:\Program Files\AcademiaFutbol\config.ini` existe y `path` apunta a `OneDrive\Academia\academia.db`
- [ ] Doble clic `AcademiaFutbol.exe` abre sin error `DB_PATH`
- [ ] Login `admin` / `admin123` → **obliga cambio de contraseña** `auth_service:73` (hash bcrypt)
- [ ] `Configuración` muestra precios `Inscripción 100, Mensualidad 100, Reingreso 100, Uniforme 20, Tasa 15, Arbitraje 15, Pago profesor 200`
- [ ] `Estudiantes` → 0 alumnos (BD virgen) — registrar 1 alumno prueba descuenta `CAMISETA-ENT` 50→49 visible en `Inventario`
- [ ] `OneDrive` icono verde (no `academia (conflicto).db`) · `PRAGMA journal_mode=WAL`

### Paso 5: Segundo PC (validación central)
Repetir wizard en PC 2 con misma cuenta OneDrive sincronizada:
- `Probar conexión` implícita: `Main` lee `OneDrive\Academia\academia.db` con alumno creado en PC1
- Login `admin` (o crear `secretaria`) → `Estudiantes` ve alumno + `Inventario` stock 49 en ambas

---

## 2. Instalación sin Inno Setup (portable ZIP)

### Paso 1: Descargar ZIP desde GitHub Release
`AcademiaFutbol-v1.0.0.zip` (56 MB)

### Paso 2: Extraer
1. Crear `C:\AcademiaFutbol\`
2. Descomprimir ZIP completo (mantener `_internal\` y `AcademiaFutbol.exe` juntos)
3. **No copiar** `academia.db` ni `config.ini` manualmente — se generan

### Paso 3: Inicializar OneDrive manual (si wizard no usado)
```bat
xcopy AcademiaFutbol C:\AcademiaFutbol\ /E
echo [database] > C:\AcademiaFutbol\config.ini
echo path=C:\Users\%USERNAME%\OneDrive\Academia\academia.db >> C:\AcademiaFutbol\config.ini
echo [backup] >> C:\AcademiaFutbol\config.ini
echo dir=C:\Users\%USERNAME%\OneDrive\BackupsAcademia >> C:\AcademiaFutbol\config.ini
mkdir "%USERPROFILE%\OneDrive\Academia\fotos"
mkdir "%USERPROFILE%\OneDrive\Academia\comprobantes"
mkdir "%USERPROFILE%\OneDrive\BackupsAcademia"
C:\AcademiaFutbol\AcademiaFutbol.exe
```

### Paso 4: Acceso directo
Clic derecho `AcademiaFutbol.exe` → `Crear acceso directo` → mover a Escritorio

---

## 3. Ejecutar desde código fuente (Desarrolladores)

### Requisitos
- Python 3.13+ · pip · OneDrive opcional

### Pasos
```bash
git clone https://github.com/MoisesVillar19/AcademiaFutbol.git
cd AcademiaFutbol
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
# DB_PATH resuelve: config.ini → OneDrive\Academia\academia.db → database\academia.db fallback
```

---

## 4. Construir ejecutable e instalador (Desarrolladores)

```bash
# 1. Ejecutable (2-3 min)
build.bat
# → dist\AcademiaFutbol\AcademiaFutbol.exe + _internal\VERSION + assets\images\logo_roncalli.png
# Verifica: dist sin academia.db ni config.ini (AcademiaFutbol.spec:104 COLLECT)

# 2. Instalador (requiere Inno Setup 6.7+)
installer\build_installer.bat
# → installer\Output\AcademiaFutbol-Setup-1.0.0.exe
# En este proyecto: normalizar si queda en installer\installer\Output\ → copiar a installer\Output\

# 3. ZIP Release
Compress-Archive -Path dist\AcademiaFutbol\* -DestinationPath AcademiaFutbol-v1.0.0.zip -Force
```

**Regla de oro `despliegue_produccion.md:192`:** `dist` y `installer\Output` **nunca** llevan `academia.db` ni `config.ini` fijo. Se generan en PC destino.

---

## 5. ¿Qué hacer con el Setup? (GitHub Release)

> **No hacer `git add` del `.exe` ni `.zip`** — están ignorados (`.gitignore:17` `*.zip`, `installer/Output/`). Se publican como **Assets de Release**, no como código.

### Flujo publicación `publicacion_release.md:3`

```bash
# 1. Versión y changelog
echo 1.0.0 > VERSION
# editar docs/desarrollo/changelog.md

# 2. Commit + push código (sin binarios)
git add docs/ VERSION AcademiaFutbol.spec installer/setup.iss
git commit -m "feat: v1.0.0 BD virgen producción OneDrive + wizard"
git push origin main

# 3. Tag
git tag v1.0.0
git push origin v1.0.0

# 4. GitHub → Releases → Draft a new release
#    - Tag: v1.0.0 · Title: v1.0.0 · Description: copiar changelog
#    - Arrastrar assets:
#      • AcademiaFutbol-Setup-1.0.0.exe (42 MB) — instalador wizard
#      • AcademiaFutbol-v1.0.0.zip (56 MB) — portable
#    - Publish release
```

**SECRETARIA recibe update automático:** `main.py:344` `after(2000, verificar_y_mostrar)` cada 24h `updater/config.py:1` `GITHUB_REPO` compara `VERSION` → diálogo `Nueva versión v1.1.0 → Descargar`.

Si el repo es privado, el updater requiere `GITHUB_REPO` público o token.

### Alternativas si no usas GitHub
- Compartir `AcademiaFutbol-Setup-1.0.0.exe` por OneDrive (carpeta compartida) / USB / correo
- El ZIP portable para PCs sin permiso de instalación

---

## 6. Configuración OneDrive (detalle)

### Si OneDrive sincronizado (recomendado prod)
`utils/constants.py:72` resuelve `DB_PATH` → `OneDrive\Academia\academia.db`:
```
C:\Users\{user}\OneDrive\Academia\academia.db        (BD central WAL)
C:\Users\{user}\OneDrive\Academia\fotos\             (FOTOS_DIR)
C:\Users\{user}\OneDrive\Academia\comprobantes\      (COMPROBANTES_DIR)
C:\Users\{user}\OneDrive\BackupsAcademia\            (BACKUP_DIR, backups cada 6h)
```
Permisos OneDrive: `ADMIN` full, `SECRETARIA` edit (misma carpeta `Academia` compartida). Verificar icono verde sincronizado tras crear alumno.

### Si OneDrive no instalado (fallback dev)
```
C:\Program Files\AcademiaFutbol\database\academia.db  (local por PC, no central)
C:\Program Files\AcademiaFutbol\backups\
```
Wizard deja aviso `Instalar OneDrive recomendado` pero permite instalar.

### Restaurar backup de prueba (si necesitas ver datos antiguos)
```bat
copy "C:\Users\%USERNAME%\OneDrive\BackupsAcademia\academia_TEST_20260906_210703.db" "C:\Users\%USERNAME%\OneDrive\Academia\academia.db" /Y
xcopy "C:\Users\%USERNAME%\OneDrive\BackupsAcademia\fotos_TEST_20260906_210703" "C:\Users\%USERNAME%\OneDrive\Academia\fotos" /E /Y
```

---

## 7. Primer arranque (BD virgen)

1. Ejecutar acceso directo → `Login`
2. `admin` / `admin123` → obliga `Cambiar contraseña` `auth_service:73`
3. `Configuración` (ADMIN) verificar 8 secciones: precios flexibles, mora, categorías `3-5..16-18`, tipos uniforme `Entrenamiento/Competencia/Completo/Media` (seed 4)
4. Registrar alumno prueba → `Ventas` `UNIFORME` stock `50→49` → cerrar y reabrir en 2ª PC y verificar `49`

---

## 8. Actualizaciones automáticas

- `.exe` nuevo **no borra** `OneDrive\Academia\academia.db` / `fotos/` / `comprobantes/` / `config.ini` (`constants.py:9` `APP_DIR` vs `_internal`, `updater/update_service.py` excluye `database/`)
- BD migra con `create_db.py:379` `_migrar_columnas_faltantes` `ALTER ADD COLUMN IF NOT EXISTS` (ej `1.0.0→1.1.0` `egreso.activo`)
- Rollback: desinstalar y reinstalar `Setup-X.Y.Z.exe` anterior; BD intacta

---

## 9. Desinstalar

### Con Inno Setup
Panel de Control → Programas y características → `AcademiaFutbol` → Desinstalar → wizard (no borra `OneDrive\Academia\academia.db` ni `BackupsAcademia`)

### Portable
Eliminar carpeta `C:\AcademiaFutbol\` + acceso directo

---

## 10. Solución de problemas

| Problema | Causa | Solución |
|---|---|---|
| `database is locked` | 2 PCs escriben sin sync OneDrive | Esperar icono verde, WAL + `transaccion:43` reintenta |
| `academia (conflicto).db` | Edición offline simultánea | Cerrar apps, OneDrive resuelve, restaurar `academia_TEST_*.db` |
| `No se encontró OneDrive` | OneDrive no instalado | Instalar OneDrive o usar fallback local |
| `admin123` no entra | Ya cambió contraseña | Usar nueva o PIN emergencia `roncalli2026` `seed:64` |
| Foto no se ve | `FOTOS_DIR` sin permiso | Verificar `OneDrive\Academia\fotos` existe y `PIL` instalado |

---

*PDF generado desde este markdown para entrega. Artefactos listos en `installer/Output/` y `AcademiaFutbol-v1.0.0.zip`.*
