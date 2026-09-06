# AcademiaFutbol — Sistema de Gestión v2 (Flexible + OneDrive Central)

> **Academia Deportiva Roncalli.** Matrículas, cuotas, pagos, **ventas (uniformes/tienda/campeonato)**, inventario con `tipo_uniforme`, **egresos**, reportes `Ingresos vs Egresos`, auditoría, backups. **BD central en `OneDrive\Academia\academia.db`** (“web sin ser web”) + **precios 100% configurables sin código**.

[![Versión](https://img.shields.io/badge/versión-1.0.0-blue)]()  `VERSION` + `docs/desarrollo/changelog.md`

### Inicio rápido (3 pasos)

1. **OneDrive:** Asegúrate que OneDrive esté sincronizado (icono verde). Ejecuta **`setup_onedrive.bat`** (doble clic) → crea `OneDrive\Academia\`, `fotos\`, `comprobantes\`, `BackupsAcademia\` y `config.ini` con `DB_PATH=OneDrive\Academia\academia.db`.
2. **App:** `py main.py` (dev) o `AcademiaFutbol-Setup-1.0.0.exe` (installer) → sigue wizard 6 pasos → `Probar conexión` ✔ → `Abrir`.
3. **Login:** `admin / admin123` → cambia clave (queda al frente/centrada, fondo Dashboard no queda blanco) → `Configuración` verifica `Inscripción 100 / Uniforme 20`.

> Sin OneDrive: `config.ini` fallback `database\academia.db` local.

### Estructura del proyecto

```
AcademiaFutbol/
├── main.py + VERSION + config.ini (generado) + config_visual.json
├── setup_onedrive.bat       # Configura OneDrive central en cada PC
├── database/  connection.py, create_db.py (18+4 tablas v2), seed.py, backup.py, restore.py
├── models/  18+4 dataclass (@dataclass) — tipo_uniforme, venta, egreso
├── repositories/  18+4 — solo INSERT/UPDATE/SELECT, soft delete activo=0
├── services/  venta_service, egreso_service, tipo_uniforme_service, cuota (mora), pago (comprobante)
├── controllers/  login, estudiante, matricula (diferir), pago, venta, egreso, inventario, configuracion (7 precios)
├── views/  login (topmost), dashboard (14 cards), estudiantes (foto 60), matriculas (diferir), pagos (comprobante), ventas, egresos, inventario (compra/venta/ganancia), configuracion (8 secciones), reportes (9), auditoria
├── utils/  constants.py (OneDrive detect + DB_PATH), validators, security (bcrypt), ui_helpers (hover), dates, logger
├── widgets/ date_picker.py (escribir YYYY-MM-DD o click Día/Mes/Año + Hoy)
├── assets/images/logo_roncalli.png
├── installer/  setup.iss (Inno, crea OneDrive + config.ini solo si no existe), build_installer.bat
├── updater/  update_service.py (excluye database/*.db, config.ini, logs)
├── docs/  sistema/ (reglas, arquitectura, diccionario, casos, convenciones) + desarrollo/ + despliegue/ + manuales/ + testing/
└── DAYANNA_REVISION.md  # Checklist 13 módulos para probar a mano + opencode
```

### Documentación

Ver `docs/README.md` índice:

- `docs/sistema/reglas_negocio.md` RN-001..050 + `desarrollo/cambios_RN_v2.md` (precios flexibles)
- `docs/sistema/arquitectura_bd.md` + `diccionario_datos.md` (DDL `create_db.py:4`)
- `docs/despliegue/despliegue_produccion.md` **plan build que no rompe** (11+13 checklist) + `setup_onedrive.bat`
- `docs/manuales/manual_sistema.md` (ADMIN/SECRETARIA paso a paso)
- `docs/DAYANNA_REVISION.md` (checklist Dayanna)

Prioridad: `AGENTS.md > sistema/reglas_negocio > arquitectura_bd > diccionario > arquitectura_software`

### Flujos clave (flexibles, sin código)

- **Nuevo:** `Estudiantes → foto → Matrícula (precio_inscripcion 100)` → auto `-1 Camiseta Entrenamiento` stock + `Venta INSCRIPCION` + cuota `PENDIENTE`
- **Reingreso:** `Retirar → Reingresante → Reingreso` → dialog `¿Vender uniforme?` → `Ventas UNIFORME` aparte (precio por tipo 20/30)
- **Mensualidad:** `Monto pactado` o `tarifa` + `beca PORCENTAJE/MONTO_FIJO` (múltiple si `permitir=1`) → `cuota.monto_total` + `diferir 2-3` genera N cuotas; asignar beca después recalcula `PENDIENTE`
- **Pagos:** `YAPE` exige `comprobante` → `OneDrive\comprobantes\{recibo}.jpg`; `PARCIAL→PAGADO` auto siguiente mes
- **Precios:** todo en `Configuración` `ADMIN` (`precio_inscripcion/mensualidad/reingreso/uniforme` etc.)

### Instalación

**Recomendado OneDrive central (N PCs, BD no se mueve):**
```
# PC1 ADMIN
setup_onedrive.bat
py main.py  # o AcademiaFutbol.exe

# PC2+ SECRETARIA: mismo bat + misma cuenta OneDrive compartida
```

**Instalador:** `build.bat` → `dist\` (sin `academia.db`) → `installer\build_installer.bat` → `Output\Setup-1.0.0.exe` (crea OneDrive + `config.ini` solo si no existe) + `assets`.

**Actualizar:** `GitHub Release ZIP` `AcademiaFutbol-v1.1.0.zip`; `main.py:344` check 24h → `updater` extrae **excluyendo** `database/*.db`, `config.ini`, `logs`.

### Requisitos

- Windows 10/11, OneDrive, Python 3.13 (dev), `pip install -r requirements.txt` (`customtkinter`, `bcrypt`, `openpyxl`, `reportlab`, `Pillow`, `matplotlib` opcional)
- 4 GB RAM, 500 MB disco

### Roles

- **ADMIN:** Usuarios, Configuración (7 precios, mora, tipos uniforme), Categorías/Tarifas/Becas, Auditoría, Backups/Restore, Egresos, Importar
- **SECRETARIA:** Estudiantes (foto)/Apoderados (máx 2, 1 principal)/Matrículas/Pagos (comprobante)/Ventas/Inventario/Dashboard/Reportes

### Troubleshooting

- `Database is locked` → OneDrive no verde → esperar sync `WAL`
- `academia (conflicto).db` → 2 PCs offline simultáneo → restaurar último `BackupsAcademia\academia_*.db` via `database/restore.py`
- Foto >2MB → rechaza, `PIL` no instalado → `pip install pillow`

### Licencia

Privado — Academia Deportiva Roncalli. Ver `docs/desarrollo/changelog.md`.
