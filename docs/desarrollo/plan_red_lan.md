# Plan Red LAN — 4 PCs, BD única compartida (A+C)

> Decisión: **Opción A + C**. Sin copias, sin merges. Contingencia honesta
> sin auto-merge. OneDrive descartado (permisos).

## 1. Topología

```text
PC1 (servidor) ── recurso compartido \\PC1\Academia\
│                    ├─ academia.db        (ÚNICA, seed una sola vez)
│                    ├─ fotos\             (central)
│                    ├─ comprobantes\      (central)
│                    └─ BackupsAcademia\   (central)
├── PC2 ─── abre directo ──┐
├── PC3 ─── abre directo ──┤── mismo archivo vía UNC
└── PC4 ─── abre directo ──┘   (otro router: IP fija + SMB/445, ver §6)
```

- Cada PC tiene su `config.ini` apuntando al **mismo** `path` UNC.
- Fotos/comprobantes/backups también centrales (`[rutas]` + `[backup]`).
- Seed idempotente: una sola semilla efectiva (verificado).

## 2. Decisiones técnicas

| Tema | Decisión | Por qué |
|---|---|---|
| Acceso | Directo al archivo compartido | Sin merges; AUTOINCREMENT colisionaría entre copias |
| Journal | `DELETE` en red, `WAL` en local | WAL sobre SMB = corrupción (docs SQLite) |
| Concurrencia | `busy_timeout` 20s (reintento interno SQLite) | Cobros simultáneos habituales: espera, no error |
| Cierre | Cancelar timers + checkpoint + `close_connection` + `destroy` + `sys.exit(0)` | Evita proceso zombi y `-wal` huérfanos que impiden reabrir |
| Contingencia | Snapshot local solo-lectura + re-digitación manual | Auto-merge = Opción B con sus riesgos; no se vende |
| Distribución | ZIP + Setup v1.0.3 con `setup_red.bat` incluido | PCs bloqueadas usan ZIP |

## 3. Cambios por archivo

- R1 `database/connection.py`: `es_ruta_red()`, journal adaptativo,
  `busy_timeout`, `cerrar_limpio(checkpoint)`.
- R1 `main.py` + login/cambiar_password: `_on_cerrar` endurecido.
- R2 `setup_red.bat` (nuevo): crea carpetas, escribe `config.ini`,
  verifica R/W, no crea BD huérfana.
- R2 Configuración UI: campo Ruta BD + Examinar… + Probar conexión;
  guardián anti-huérfana al arrancar.
- R3 Detección share caído + modo lectura + docs
  (`despliegue_red.md`, sección en `manual_flujos.md`).
- R4 `AcademiaFutbol.spec` hiddenimports + rebuild + SHA256 + release v1.0.3.

## 4. Riesgos y mitigación

| Riesgo | Probabilidad | Mitigación |
|---|---|---|
| Lock breve en cobro simultáneo | Media | Timeout+reintento (1–3s, sin pérdida) |
| Servidor apagado | Media (asumido) | Mensaje claro + lectura local + re-digitación + backups por PC |
| Corte de red a media venta | Baja | Transacción atómica: todo o nada; reintentar |
| 4ª PC no ve el share (otro router) | Media | Checklist §6; si no hay caso, esa PC opera local temporal + reingreso manual |
| Proceso zombi retiene `.db` | Baja (con R1) | Apagado limpio + matar proceso en Task Manager como último recurso |

## 5. Matriz de pruebas red (antes del release)

- [ ] 2 PCs cobran al mismo tiempo (pagos + ventas) sin errores ni duplicados.
- [ ] Servidor apagado → mensaje claro + modo lectura (no cuelgue, no BD huérfana).
- [ ] Corte de red a media venta → rollback limpio, reintento OK al volver.
- [ ] Cerrar con X → proceso termina (no queda en Task Manager) → reabre OK.
- [ ] Recibos correlativos únicos con uso simultáneo.
- [ ] Restaurar backup con PIN sobre el share.
- [ ] ZIP en PC bloqueada: `setup_red.bat` + arranque sin admin.

## 6. Checklist red externa (4ª PC / routers)

1. IP fija (o reserva DHCP) en PC1; anotar `\\IP\Academia`.
2. Regla firewall: SMB TCP/445 entrante en PC1 (red privada).
3. Misma credencial de Windows o usuario dedicado con permiso total al recurso.
4. Probar desde PC4: `dir \\IP\Academia` + crear/borrar archivo de prueba.
5. Opcional: mapear unidad persistente (`net use Z: \\IP\Academia /persistent:yes`).
6. Si el router aísla clientes (AP isolation): desactivar o cablear.
