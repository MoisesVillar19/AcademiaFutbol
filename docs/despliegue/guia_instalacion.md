# Guía de instalación — Academia Deportiva v1.0.3

> Para secretarias y encargados. Sin tecnicismos: qué descargar, dónde dar
> clic y qué hacer si Windows se queja. Tiempo estimado: 10 minutos por PC.

---

## 1. ¿Qué archivo uso: Setup o ZIP?

| Tu caso | Usa |
|---|---|
| Tienes permiso de administrador en la PC | **Setup** (`AcademiaFutbol-Setup-1.0.3.exe`, 40 MB) |
| PC bloqueada, cabina, sin admin, o el antivirus borra el Setup | **ZIP** (`AcademiaFutbol-v1.0.3.zip`, 54 MB) |
| Ya tienes una versión anterior instalada | Cualquiera: el actualizador migra solo (ver §6) |

Ambos contienen el mismo programa. Los descargas desde **GitHub Releases**
o los recibes por USB del encargado.

**Verifica que no estén corruptos (opcional, 1 minuto):**
1. Abre PowerShell en la carpeta del archivo.
2. Ejecuta: `certutil -hashfile AcademiaFutbol-Setup-1.0.3.exe SHA256`
3. Compara con el hash publicado en el Release:
   `9dd7c5403671f03e66b6cd6c37559c9212268489aaa60fdd365b57945591e5c0`
   (ZIP: ver hash en `SHA256-v1.0.3.txt` del Release)

---

## 2. Instalación con Setup (con permiso de admin)

1. Doble clic en `AcademiaFutbol-Setup-1.0.3.exe`.
2. Si sale la pantalla azul **"Windows protegió su PC"**: clic en
   **Más información** → **Ejecutar de todas formas**. Es normal: el programa
   no tiene firma de pago, pero es legítimo (ver §5).
3. Siguiente → carpeta (`C:\Program Files\AcademiaFutbol`) → Instalar.
4. Marca **Crear acceso directo** si quieres ícono en el escritorio → Finalizar.
5. Abre desde el acceso directo y sigue con el §4 (conectar a la red).

## 3. Instalación con ZIP (sin admin)

1. **Primero desbloquea el ZIP**: clic derecho → Propiedades → marcar
   **Desbloquear** → Aplicar. (Si no, Windows puede bloquear el programa.)
2. Clic derecho → **Extraer todo…** en `C:\AcademiaFutbol\`
   (o en Documentos). Importante: que `AcademiaFutbol.exe` y la carpeta
   `_internal` queden **juntos**, no los separes.
3. Entra a la carpeta y ejecuta `setup_red.bat` (viene incluido) — ver §4.
4. Doble clic en `AcademiaFutbol.exe`. Opcional: clic derecho →
   **Crear acceso directo** → Escritorio.

## 4. Conectar las 4 PCs (una sola base de datos) — LEER CON CALMA

Hay **dos carpetas distintas**, no las confundas:

| | Carpeta del PROGRAMA | Carpeta de DATOS (la que se comparte) |
|---|---|---|
| Qué es | Donde vive `AcademiaFutbol.exe` | Donde vive `academia.db` + fotos + comprobantes + backups |
| Dónde está | Cada PC la suya: `C:\Program Files\AcademiaFutbol\` (Setup) o `C:\AcademiaFutbol\` (ZIP) | **Solo en la principal**: ej. `C:\AcademiaDatos\`, compartida como `\\PC1\AcademiaDatos` |
| ¿Se comparte? | **NO, jamás** | **SÍ, una sola vez** |
| Nombre sugerido | `AcademiaFutbol` (ya viene así) | `AcademiaDatos` (distinto a propósito, para no confundir) |

**Nunca copies el archivo `academia.db` entre PCs** (se pierden datos).
La BD **apunta** a la carpeta compartida mediante un `config.ini` en cada PC.

### 4.1 Si YA existe una carpeta compartida con la base de datos

No crees otra. Úsala tal cual:
1. Verifica que dentro esté `academia.db` (y carpetas `fotos`, `comprobantes`).
2. Anota su dirección (ej. `\\PC1\Academia`) y úsala en el paso 4.3.
3. `setup_red.bat` **conserva** la BD existente: solo escribe el `config.ini`
   que apunta hacia ella. Jamás la borra ni la reemplaza.
4. Si hay **dos** compartidas: quédate con la que tenga los datos reales
   (la más reciente/grande), apunta todas las PCs a esa y deja de compartir
   la otra.

### 4.2 Si NO existe: crearla en la PC principal (una sola vez)

1. Crea `C:\AcademiaDatos` → clic derecho → **Compartir** (permiso total para
   las demás PCs). Anota la dirección, ej. `\\PC1\AcademiaDatos`.
2. Permite SMB en el firewall (el técnico: TCP/445 entrante, red privada).
3. La primera vez que abras la app apuntando ahí, ella sola crea `academia.db`
   con los datos iniciales (una sola vez para las 4 PCs).

> ¿Y si antes compartiste la carpeta del **programa** (la del .exe)?
> Quítale el compartido: clic derecho → Compartir → Quitar/Dejar de compartir.
> Esa carpeta es por PC y no debe verse en red (permisos, bloqueos y
> actualizaciones fallan si se comparte). Comparte **solo** la de datos.

### 4.3 En cada PC (incluida la principal): apuntar a la compartida

Vale igual para instalación **Setup y ZIP**: el `setup_red.bat` viene en
ambos (ZIP en la raíz, Setup en Program Files) y el `config.ini` funciona
idéntico en los dos casos.

1. Doble clic en `setup_red.bat`.
2. Escribe la dirección de datos: `\\PC1\AcademiaDatos`
   (o la IP, ej. `\\192.168.1.50\AcademiaDatos`, o tu carpeta existente del §4.1).
3. Debes ver **OK lectura** y **OK escritura**. El script deja todo apuntando
   al mismo lugar. ¿Qué escribió? un `config.ini` al lado del `.exe` con:
   `[database] path=\\PC1\AcademiaDatos\academia.db` (+ backup y fotos).
4. Si dice que no accede: revisa que la principal esté **encendida**,
   conectada a la red y con la carpeta compartida (§7). **No sigas**: sin
   acceso, la app no debe crear datos locales.

**Alternativa manual:** Configuración (ADMIN) → Respaldo → campo
*Base de datos en uso* → 📁 Examinar… → elige `academia.db` **de la carpeta
compartida** → 💾 Guardar ruta → **Probar conexión** (debe decir OK) →
reinicia la app.

## 5. Primer arranque

1. Usuario: `admin` · Contraseña: `admin123` (te obligará a cambiarla).
2. Crea los usuarios de secretaría (ADMIN → Usuarios): rol SECRETARIA.
3. Configuración → verifica nombre de la academia, precios en **Tarifas**
   (ya vienen migrados), tackle **Probar conexión** en Respaldo.
4. Cobra una venta de prueba y anúlala/revísala para confirmar que todo graba.

## 6. Actualizaciones (ya no reinstales a mano)

- El programa avisa solo cuando hay versión nueva (revisa cada 24h).
- Ventana con **barra de progreso** (%, MB, velocidad, tiempo restante),
  botones **Actualizar / Cancelar / Reintentar**.
- Si estás en Program Files pedirá **permiso de Administrador (UAC)**:
  es normal, dale Sí. En portable no pide nada.
- Forzar revisión: Configuración → Actualizaciones → **Buscar ahora**.

## 7. Si algo se bloquea (soluciones por caso)

| Síntoma | Solución |
|---|---|
| Pantalla azul SmartScreen | Más información → Ejecutar de todas formas (§2) |
| Antivirus lo borra ("amenaza") | Seguridad de Windows → Historial → Permitir; agrega la carpeta como **Exclusión**; vuelve a descargar |
| "No se puede ejecutar" tras descargar | Clic derecho → Propiedades → Desbloquear (o `Unblock-File` en PowerShell) |
| Sin permiso de admin | Usa el **ZIP** (§3), no pide permisos |
| "No se puede acceder a la base de datos" | Enciende la PC principal, revisa red y recurso compartido (§4) |
| La app no vuelve a abrir | Administrador de tareas → terminar `AcademiaFutbol.exe` → abrir de nuevo |
| Cobro simultáneo lento 1–3s | Normal: la segunda PC espera su turno, no se pierde nada |

## 8. Para el encargado (checklist por PC)

- [ ] Setup o ZIP instalado + acceso directo.
- [ ] `setup_red` OK (lectura + escritura) o Probar conexión OK.
- [ ] Login admin + password cambiada + usuarios SECRETARIA creados.
- [ ] Tarifas revisadas (precios migrados solos desde la versión anterior).
- [ ] Backup: frecuencia en 1 día; ruta = carpeta compartida.
- [ ] PIN de emergencia anotado fuera del sistema.
- [ ] Probar: cobrar + pagar + restaurar de prueba un día sin público.

> Detalle técnico completo: `despliegue_red.md` (topología, firewall, matriz
> de pruebas) y `plan_red_lan.md` (decisiones). Flujos del sistema:
> `manuales/manual_flujos.md`.
