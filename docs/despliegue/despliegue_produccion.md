# Despliegue a Producción — AcademiaFutbol (BD Centralizada en OneDrive, "Web sin ser web")

> **Objetivo:** App local `Python + CustomTkinter + SQLite` que funciona en **N PCs** contra **1 BD central en OneDrive** que no se mueve. Instalación segura por wizard y actualizaciones automáticas. Arranque desde 0 sin BD legado, **sistema flexible 100% configurable**.
> **Relacionado:** `cambios_RN_v2.md` (RN-036..050 flexible), `instalacion.md`, `publicacion_release.md`, `AcademiaFutbol.spec`, `updater/config.py`.

### 1. Arquitectura de despliegue (OneDrive)

```
PC 1 (SECRETARIA) ─┐
PC 2 (SECRETARIA) ─┼─►  C:\Users\{user}\OneDrive\Academia\academia.db  (SQLite central, WAL+FK ON)
PC 3 (ADMIN) ──────┘         ▲                    │
                              │              OneDrive\BackupsAcademia\  (backups)
                           config.ini ──►  OneDrive\Academia\fotos\ + comprobantes\ (compartido)
                                              ▲
                                         GitHub Releases (updater)
```

**Actual:** `utils/constants.py:34` `DB_PATH=APP_DIR/database/academia.db` local por PC. **Objetivo:** `DB_PATH=OneDrive\Academia\academia.db` detectado por `constants.py:97` `detectar_onedrive()` → `BACKUP_DIR` ya lo hace; extender a `DB_PATH` vía `config.ini` wizard.

**Principio:** View→Controller→Service→Repository→`database/connection.py:21` único; Repos usan SQL parametrizado `?` — cambiar solo `connection.py` y `constants.py`, cero cambios Services. `RN-029` precios y `RN-025` tipos uniforme 100% configurables sin código.

### 2. Opciones para BD central y recomendación (OneDrive como eje)

| Opción | Cuándo usar | Pros | Contras |
|---|---|---|---|
| **A. SQLite en OneDrive** `OneDrive\Academia\academia.db` **(recomendada para tu caso)** | ≤5 PCs, OneDrive sincronizado, "bd no se mueve", acceso fácil | 0 cambios Services/Repos; `connection.py:27` solo cambia `DB_PATH` a OneDrive; `constants.py:97` ya detecta OneDrive; instalador simple; wizard funcional | Locks OneDrive frágiles si 2 PCs escriben offline y sincroniza después (conflicto `academia (conflicto).db`); mitigar con `WAL` + aviso `transaccion:43` |
| **B. SQLite en carpeta SMB** `\\SERVIDOR\Academia\` | LAN con NAS y sin OneDrive | Similar A, pero sin dependencia nube | Requiere servidor siempre encendido |
| **C. Servidor BD `PostgreSQL/MySQL`** | >5 PCs o fuera de LAN/internet | Pool real, `RN-028 soft delete` fiable | Migrar driver `?`→`%s`, 1-2 días |
| **D. Híbrido offline + sync** | PCs sin red | SQLite local + push `main.py:231` | Complejo |

**Recomendación consolidada (desde 0, flexible):** **A OneDrive** — cumple "bd no se mueve, acceso a datos fácil, subir datos como web sin ser web, local". `config.ini` wizard deja PC funcional en 6 pasos (ver §4). Ruta a **C** si crece.

### 3. Configuración centralizada y flexible (sin `.env` en prod, todo en `CONFIGURACION`)

| Entorno | Archivo | Contenido | Git |
|---|---|---|---|
| Dev | `.env` + `.env.example` | `DEFAULT_ADMIN_PASS=admin123`, `PIN_EMERGENCIA=...`, `DB_NAME=academia.db` | `.env` ignorado, `.env.example` commiteado |
| Prod | `APP_DIR/config.ini` generado por wizard | `DB_PATH=OneDrive\Academia\academia.db`, `BACKUP_DIR=OneDrive\BackupsAcademia`, `FOTOS_DIR=OneDrive\Academia\fotos` | No en repo; permisos solo ADMIN local |
| BD | `configuracion` tabla `RN-029` `RN-047` | `precio_inscripcion 100, precio_mensualidad 100, precio_reingreso 100, precio_uniforme 20, paquete 20/30, dias_por_vencer 3, permitir_multiples_becas 1` + descuentos `beca` | Central, editable ADMIN sin deploy |

`utils/constants.py:34` leer en orden: `config.ini` si existe → `os.getenv("DB_PATH")` → `OneDrive\Academia\academia.db` (detectado `detectar_onedrive:86`) → `APP_DIR/database/academia.db` fallback dev. `utils/logger.py:4` `LOG_DIR=APP_DIR/logs` local. Todo precio/descuento/tipo uniforme flexible sin hardcode.

**Wizard no pide `.env` al usuario** — lo genera. `seed.py:32` lee `config.ini`/env para admin inicial, hashea con `bcrypt`.

### 4. Instalador wizard (Inno Setup) — Pasos para dejar PC funcional (énfasis)

**Requisitos:** `AcademiaFutbol.spec:104` `COLLECT` genera `dist/AcademiaFutbol/`, `installer/build_installer.bat` + Inno Setup 6.7. **OneDrive debe estar instalado y sincronizado** (ver `constants.py:86`).

**Pasos wizard detallados (deja funcional en 6 pasos):**

1. **Bienvenida** — `AcademiaFutbol v1.0.0` → `Siguiente`
2. **Licencia** → Aceptar → `Siguiente`
3. **Carpeta** `C:\Program Files\AcademiaFutbol\` (editable) → `Siguiente`
4. **BD central OneDrive (pantalla nueva clave):**
   - Campo `Ruta BD` default autodetectado `C:\Users\{user}\OneDrive\Academia\academia.db` (`detectar_onedrive:86`); editable si OneDrive en otra ruta.
   - `Ruta Backups` default `OneDrive\BackupsAcademia\`
   - `Carpeta fotos` default `OneDrive\Academia\fotos\` + `comprobantes\`
   - Botón **`Probar conexión`** → ejecuta `fetch_one("SELECT 1")` (`connection.py:74`); muestra `✔ Conexión OK` o `✘ No se encontró — se creará al finalizar`.
   - Validación flexible: si OneDrive no detectado, avisa `Instalar OneDrive recomendado para BD central` pero permite `APP_DIR/database` local (fallback).
5. **Acceso directo** → marcar `Crear en escritorio` → `Siguiente`
6. **Instalar** → copia `dist/` + escribe `config.ini` (`[database] path=...`, `[backup] dir=...`, `[fotos] dir=...`) + `VERSION` → **Finalizar** → `✔ Abrir AcademiaFutbol ahora` (deja funcional).

**Qué queda funcional tras wizard:**

- `config.ini` en `C:\Program Files\AcademiaFutbol\` apunta a OneDrive; doble clic `AcademiaFutbol.exe` abre `main.py:37` `App` sin error `DB_PATH`.
- `OneDrive\Academia\academia.db` se crea vacía al primer arranque `create_tables:237` + `seed:46` categorías `3-5..16-18`, `tipo_uniforme` 4, Camiseta stock 50.
- `OneDrive\Academia\fotos\` y `comprobantes\` listos para `RN-041/042`.

**Inno `.iss` extracto:**

```ini
[Files]
Source: "dist\AcademiaFutbol\*"; DestDir: "{app}"; Flags: recursesubdirs
[INI]
Filename: "{app}\config.ini"; Section: "database"; Key: "path"; String: "{code:GetDBPath}"
Filename: "{app}\config.ini"; Section: "backup"; Key: "dir"; String: "{code:GetBackupPath}"
Filename: "{app}\config.ini"; Section: "fotos"; Key: "dir"; String: "{code:GetFotosPath}"
[Run]
Filename: "{app}\AcademiaFutbol.exe"; Description: "Abrir AcademiaFutbol"; Flags: postinstall nowait
[Code]
function GetDBPath(S: String): String; begin Result := ExpandConstant('{userdocs}\OneDrive\Academia\academia.db'); end;
```

**Sin Inno (manual funcional):**

```bat
xcopy dist\AcademiaFutbol C:\AcademiaFutbol\ /E
echo [database] > C:\AcademiaFutbol\config.ini
echo path=C:\Users\%USERNAME%\OneDrive\Academia\academia.db >> C:\AcademiaFutbol\config.ini
mklink /D "C:\AcademiaFutbol\logs" "C:\Users\%USERNAME%\OneDrive\Academia\logs"
AcademiaFutbol.exe
```
(ver `instalacion.md:36` para alternativa).

**Verificación deja funcional (checklist instalación):**

- [ ] `config.ini` existe y `DB_PATH` apunta a OneDrive
- [ ] Primer arranque `admin/admin123` → obliga cambio `auth_service:73` OK
- [ ] `Configuración` muestra `precio_inscripcion 100`, `precio_uniforme 20` (flexible)
- [ ] Crear alumno nuevo descuenta -1 Camiseta `RN-036` y visible en `Productos` en 2ª PC
- [ ] `OneDrive` icono verde sincronizado (no conflicto `academia (conflicto).db`)

### 5. Actualizaciones automáticas

`main.py:344` `after(2000, lambda: update_view.verificar_y_mostrar(app))`, `updater/config.py:1` `GITHUB_REPO`, `FRECUENCIA 24h`, `publicacion_release.md:3` flujo `VERSION → changelog → tag → Release ZIP → SECRETARIA auto-update`.

Con BD central, **el `.exe` se actualiza por PC**, la **BD no se toca** (`APP_DIR` vs `_internal` `constants.py:9`). `database/connection.py:27` `connect(factory=ConexionConTransaccion)` mantiene `WAL`.

### 6. Seguridad

- Admin inicial `admin/admin123` hasheado `seed.py:32`, `auth_service:73` obliga cambio. PIN emergencia hasheado `seed:64`, `auth_service:98` `verify_password`.
- `config.ini` solo lectura ADMIN Windows, acceso `\\SERVIDOR\Academia\` con permisos `ADMIN` full, `SECRETARIA` read/write BD pero no `config.ini`.
- `LOG` `RN-035` inmutable solo `INSERT`, `auditoria_controller:7` gate `es_admin`.

### 7. Procedimiento despliegue desde 0 (OneDrive funcional)

**Preparación central OneDrive (1 vez, ADMIN):**

```bash
# En cuenta OneDrive empresa (ej admin@roncalli.onmicrosoft.com)
OneDrive\Academia\                 # BD central
OneDrive\Academia\fotos\           # RN-041
OneDrive\Academia\comprobantes\    # RN-042
OneDrive\BackupsAcademia\          # backup_service:97
# Compartir carpeta Academia con SECRETARIA (lectura/escritura OneDrive)
# academia.db vacía se crea al primer arranque (create_tables)
# Permisos OneDrive: ADMIN full, SECRETARIA edit
```

**Build release:**

```bash
echo 1.0.0 > VERSION
# docs/cambios_RN_v2.md y despliegue ya editados con flexible + OneDrive
build.bat         # genera dist/AcademiaFutvol/
cd installer && build_installer.bat  # Output/AcademiaFutbol-Setup-1.0.0.exe (con pantalla BD OneDrive)
git add . && git commit -m "feat: v1.0.0 RN v2 flexible + OneDrive central" && git push
git tag v1.0.0 && git push origin v1.0.0
# GitHub → Release ZIP dist/
```

**Instalación por PC (deja funcional, énfasis):**

1. **PC 1 ADMIN:** Ejecutar `Setup-1.0.0.exe` → `Ruta BD` confirma `OneDrive\Academia\academia.db` → `Probar conexión` → Instalar → `Finalizar Abrir` → Login `admin/admin123` → cambiar pass obligatorio `auth_service:73` → `Configuración` verifica `precio_inscripcion 100`, `precio_uniforme 20` (flexibles) + `frecuencia_backup 7` → crear alumno nuevo prueba descuenta -1 Camiseta.
2. **PC 2 SECRETARIA:** Mismo Setup → misma `Ruta BD` (OneDrive ya sincronizó `academia.db` con alumno creado) → `Probar conexión ✔` → Instalar → Login `secretaria` → Ver alumno y stock 49 en `Productos` (central).
3. **Reingreso prueba:** PC 2 buscar `DNI` retirado → `Reingreso` → nueva `matricula precio_reingreso 100` → Venta aparte `Uniforme Competencia 25` → stock Competencia -1 visible en PC 1.

**Validación deja funcional:**

- [ ] 2 PCs simultáneas registran pago distinto sin `database is locked` (OneDrive sincroniza tras `commit WAL`)
- [ ] `fotos/` y `comprobantes/` visibles en ambos PCs (OneDrive verde)
- [ ] `backup_service:26 crear_backup` guarda en `OneDrive\BackupsAcademia\academia_YYYY-MM-DD_HH-MM-SS.db` cada 6h `main.py:242`
- [ ] `updater` detecta `v1.0.1` en 24h `updater/config.py:6`
- [ ] Descuento configurable `beca 10%` + `monto_pactado 90` aplicado sin código en nuevo alumno
- [ ] Config precios editados en PC 1 se ven en PC 2 tras reinicio (lee `configuracion` tabla central)

### 8. Operación y mantenimiento

| Tarea | Frecuencia | Cómo |
|---|---|---|
| Backup automático | `configuracion.frecuencia_backup 7` + `main.py:242` cada 6h `verificar_backup_automatico` | `backups/` OneDrive o `\\SERVIDOR` |
| Restaurar | Demanda | `database/restore.py` `shutil.copy2(backup, DB_PATH)` + `close_connection()` |
| Actualizar PCs | Por release | Publicar `v1.x` GitHub, PCs `after 24h` muestran diálogo update |
| Stock bajo | Diario | `dashboard_service:32` `stock <= minimo` |
| Logs | Diario | `APP_DIR/logs/academia.log` local por PC, no central |

### 9. Rollback

Si update falla: desinstalar `Panel Control → AcademiaFutbol`, reinstalar `Setup-X.Y.Z.exe` anterior; BD central intacta (no se borra). Si BD corrupta: `restore` último backup `academia_*.db`.

### 10. Requisitos

- Windows 10+, LAN o VPN a `\\SERVIDOR`, Inno Setup solo dev, Python 3.13 dev, `customtkinter/bcrypt/openpyxl`.

### 11. Plan de Build que no rompe (checklist obligatorio antes de cada exe)

> **Objetivo:** el `AcademiaFutbol.exe` nuevo nunca borre `OneDrive\Academia\academia.db`, `fotos/`, `comprobantes/` ni `config.ini`.

| Paso | Comando | Verifica | Si falla |
|---|---|---|---|
| 1. `VERSION` | `echo 1.1.0 > VERSION` | `type VERSION` | No tag |
| 2. `changelog` | `docs/desarrollo/changelog.md` nueva entrada | `git diff` | Release sin notas |
| 3. `DB` no hardcode | `grep -r "C:\\"` `utils/constants.py` → solo `config.ini` | `config.ini` existe | BD local hardcodeada |
| 4. `spec` completo | `AcademiaFutbol.spec:12` `datas` + `hiddenimports` incluye `venta/egreso/tipo_uniforme, ui_helpers, controllers/*` | `py -m PyInstaller --log-level WARN` sin `missing` | Build rompe ventas |
| 5. `build.bat` | `build.bat` → `dist\AcademiaFutbol\AcademiaFutbol.exe` + `assets` | `dist` no contiene `database\academia.db` (solo `_internal`) | Si lo contiene, `AcademiaFutbol.spec:104 COLLECT` mal |
| 6. `installer` | `installer\build_installer.bat` → `Output\Setup-1.1.0.exe` | `setup.iss:46` `Source: ..\dist\AcademiaFutbol\*` `createallsubdirs` pero **no** `database\academia.db` | Si lo empaqueta, sobreescribe BD central |
| 7. `setup_onedrive.bat` | `setup_onedrive.bat` crea `OneDrive\Academia\`, `fotos/`, `comprobantes/`, `config.ini` y migra `database\academia.db` si no existe `OneDrive\...` | `type config.ini` muestra `[database] path=OneDrive\...` | Wizard installer debe replicarlo |
| 8. `updater` | `updater\update_service.py` extrae ZIP a `App\` **excluyendo** `database/`, `config.ini`, `logs/`, `OneDrive` | `updater/config.py:1` `GITHUB_REPO` público | Si no excluye, update borra BD |
| 9. **Prueba local** | `py main.py` → login `admin/admin123` → `Setup OneDrive` → `Dashboard` sin `database is locked` | `OneDrive` icono verde, `academia.db` WAL | Si `locked`, revisar `PRAGMA journal_mode=WAL` |
| 10. **Prueba multi-PC** | 2 PCs `OneDrive` mismo `academia.db` → PC1 crea alumno, PC2 `Actualizar` lo ve | `SELECT COUNT(*) FROM estudiante` igual | Si no, `config.ini` apunta a local |

**Regla de oro:** `dist` y `installer\Output` **nunca** llevan `academia.db` ni `config.ini` con path fijo. `config.ini` se genera **en la PC destino** por `setup_onedrive.bat` o `setup.iss:60` `CurStepChanged`.

### 12. Versionado y migraciones futuras (no romper)

| Versión | DDL | Migración | Compatibilidad |
|---|---|---|---|
| `1.0.0` | `estudiante.foto_path`, `producto.precio_*`, `tipo_uniforme/venta/egreso`, `configuracion 7 precios` | `create_db.py:302` `_migrar_columnas_faltantes` `ALTER ADD COLUMN IF NOT EXISTS` + `seed 4 tipos` | `v1.0.0` abre `v0.9` DB vieja → `ALTER` auto, no borra datos |
| `1.1.0` | `egreso.activo` | `ALTER ADD activo DEFAULT 1` | `1.0.0 DB` → `1.1.0 exe` migra |
| `1.2.0` futuro | `producto.ganancia` | `ALTER` + `seed` | Nunca `DROP` |

**Versionado `VERSION` + `changelog.md` + `git tag v1.1.0` + `GitHub Release ZIP`** `publicacion_release.md:3`.

### 13. Checklist entrega (antes de enviar a secretaria)

- [ ] `docs/desarrollo/cambios_RN_v2.md` + este doc + `manual_sistema.md` commiteados
- [ ] `VERSION` y `docs/desarrollo/changelog.md` actualizados
- [ ] `AcademiaFutbol.spec` `datas` incluye `config.ini` (opcional) + `assets` + `hiddenimports` `venta/egreso/tipo_uniforme/ui_helpers`
- [ ] `build.bat` `dist` sin `academia.db`
- [ ] `setup_onedrive.bat` probado `OneDrive\Academia\academia.db` `fotos/`
- [ ] `installer\setup.iss` `[Dirs] {app}\database` `users-modify` pero `config.ini` generado, no empaquetado fijo
- [ ] `updater` excluye `database/` + `config.ini`
- [ ] Test `py main.py` `cambiar contraseña` al frente `2` PCs + `Dashboard Neto` no `0` si hay ventas

---

**Próximo paso:** Ejecutar `setup_onedrive.bat` en cada PC antes del primer `AcademiaFutbol.exe`, luego `build.bat → build_installer.bat` para esta última parte más importante.
