# AcademiaFutbol — Sistema de Gestión v1.0.3

> **Academia Deportiva Roncalli.** Matrículas, cuotas, pagos, ventas
> (uniformes/tienda/campeonato por división), campeonatos (inscritos,
> recaudado, arbitraje, neto), inventario, egresos, dashboard Pro
> (tablas + gráficos + comparativa MoM), reportes, auditoría con usuario,
> backups con fallback local. **BD única en red LAN**
> (`\\SERVIDOR\Academia\academia.db`) + **precios en Tarifas**.

[![Versión](https://img.shields.io/badge/versión-1.0.3-blue)]() `VERSION`

### Inicio rápido

1. **Red:** en cada PC ejecuta **`setup_red.bat "\\SERVIDOR\Academia"`**
   (verifica lectura/escritura y escribe `config.ini`).Detalle en
   `docs/despliegue/guia_instalacion.md`.
2. **App:** `py main.py` (dev) o instala `AcademiaFutbol-Setup-1.0.3.exe`
   o extrae `AcademiaFutbol-v1.0.3.zip` (portable, sin admin).
3. **Login:** `admin / admin123` → cambia la clave → crea usuarios
   SECRETARIA → verifica Tarifas y Probar conexión.

> Sin red: fallback a BD local. Nunca copies `academia.db` entre PCs.

### Estructura del proyecto

```
AcademiaFutbol/
├── main.py + VERSION + config.ini (generado)
├── setup_red.bat              # Apunta cada PC al recurso compartido
├── database/  connection.py (journal adaptativo red/local, timeout, cierre limpio),
│              create_db.py (migraciones), seed.py (idempotente), backup.py, restore.py
├── models/  dataclass (@dataclass)
├── repositories/  solo INSERT/UPDATE/SELECT, soft delete activo=0
├── services/  matricula (concepto>tarifa>monto), pago, venta (campeonato por tarifa),
│              egreso, cuota (mora), dashboard (comparativa MoM), backup (fallback local)
├── controllers/  login, estudiante, matricula, pago, venta, egreso, beca,
│                 inventario, categoria, tarifa, reporte, auditoria, importar,
│                 usuario (roles + matriz de permisos), configuracion
├── views/  dashboard Pro, estudiantes, matriculas, pagos, ventas+campeonatos,
│           egresos, inventario, tarifas+becas, usuarios+permisos,
│           reportes, auditoria (con username), configuracion, importar, login
├── utils/  constants (rutas red/local), validators, security (bcrypt),
│           ui_helpers (secciones, cards, toggle Tabla/Gráfico), dates, logger
├── widgets/  date_picker.py (escribir fecha + validación), debounce, pagination
├── installer/  setup.iss (Inno Setup), build_installer.bat, README_BLOQUEO.txt
├── updater/  dual Setup/ZIP con barra de progreso (%, MB/s, ETA)
├── docs/  sistema/ + desarrollo/ (incl. plan_red_lan.md) + despliegue/
│          (guia_instalacion.md/.pdf, despliegue_red.md) + manuales/ (.md + .pdf)
└── tools/md_to_pdf.py  # genera los PDF de la documentación
```

### Documentación

- Uso: `docs/manuales/manual_sistema.md(.pdf)` · Flujos y casos:
  `docs/manuales/manual_flujos.md(.pdf)` · Instalación:
  `docs/despliegue/guia_instalacion.md(.pdf)` · Red:
  `docs/despliegue/despliegue_red.md` · Decisiones: `docs/desarrollo/plan_red_lan.md`
- Índice: `docs/README.md`. Prioridad:
  `AGENTS.md > sistema/reglas_negocio > arquitectura_bd > diccionario > arquitectura_software`

### Flujos clave

- **Nuevo:** Estudiante 🆕 → Matrícula (tarifa/concepto/monto) → auto `-1 Camiseta` + cuota PENDIENTE
- **Reingreso:** Retirar → Reingresante → matrícula **nueva** (no reactiva)
- **Mensualidad:** tarifa por edad o monto pactado (0 = gratuito) + beca %/monto + diferir 2-3
- **Pagos:** parcial/total, YAPE exige comprobante, PARCIAL→PAGADO automático
- **Campeonato:** tarifa por división + inscripción de estudiantes + arbitraje vinculado = neto por división
- **Precios:** todo en Tarifas (ACADEMIA/CAMPEONATO/SERVICIO); egresos PROFESOR/ARBITRAJE con monto sugerido editable

### Roles

- **ADMIN:** todo (Usuarios, Tarifas+Becas, Auditoría, Configuración, Importar, Restaurar).
- **SECRETARIA:** Dashboard, Estudiantes, Matrículas, Pagos, Ventas, Campeonatos, Egresos, Inventario, Reportes, Respaldo manual. Matriz ajustable en Usuarios → Permisos por rol.

### Requisitos

- Windows 10/11, red LAN con carpeta compartida (servidor siempre encendido en horario)
- Dev: Python 3.13, `pip install -r requirements.txt`
- 4 GB RAM, 500 MB disco

### Troubleshooting

- `No se puede acceder a la base de datos` → encender servidor, revisar red/recurso
- App no reabre → terminar `AcademiaFutbol.exe` en Administrador de tareas
- Bloqueo SmartScreen/antivirus → `guia_instalacion.md` §7 (o usar ZIP)
- Dato borrado → restaurar backup con PIN (ADMIN, demás PCs cerradas)

### Licencia

Privado — Academia Deportiva Roncalli.
