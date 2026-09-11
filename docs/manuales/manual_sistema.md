# Manual del Sistema — Academia Deportiva v1.0.3

> Guía de uso diario para administradores y secretaría. Instalación y
> bloqueos: ver `guia_instalacion.md`. Paso a paso con casos:
> ver `manual_flujos.md`.

---

## 1. Qué es y cómo trabajan las 4 PCs

El programa se instala en cada PC, pero todas abren la **misma base de datos**
ubicada en la PC principal (carpeta compartida). Lo que cobra una PC lo ven
las demás al instante. Reglas de oro:

- **Nunca copies** el archivo `academia.db` entre PCs.
- Si la principal está apagada, el programa avisa y no deja operar
  (no crea datos locales silenciosos).
- Cada PC guarda respaldos automáticos; con frecuencia de 1 día siempre hay
  copia fresca.

## 2. Roles: qué puede cada uno

| Módulo | ADMIN | SECRETARIA |
|---|---|---|
| Dashboard, Estudiantes, Matrículas, Pagos, Ventas, Campeonatos, Egresos, Inventario, Reportes, Respaldo manual | Sí | Sí |
| Usuarios, Tarifas, Auditoría, Configuración, Importar, Restaurar/Rotar | Sí | No |

- Solo existen ADMIN y SECRETARIA. El ADMIN puede ajustar qué módulos ve
  SECRETARIA en **Usuarios → Permisos por rol** (ADMIN siempre ve todo).
- Primer acceso: usuario `admin`, contraseña `admin123` (te obliga a cambiarla).
- Guarda el **PIN de emergencia** fuera del sistema: restablece contraseñas.

## 3. Módulos (uso diario)

**Dashboard.** 15 tarjetas resumen; clic en cualquiera para ver tabla y
gráfico (interruptor Tabla/Gráfico/Ambos). La tarjeta MoM compara el mes
actual contra el anterior. Botón Volver para regresar.

**Estudiantes.** Lista con filtros y buscador; cada tarjeta se expande con
contacto y apoderados. Al registrar, el check **"¿Es REALMENTE nuevo?"**
solo se marca en altas nuevas reales (regala camiseta y cuenta en Nuevos
del Mes); en carga masiva de existentes va **desmarcado**. Retirar,
reingresar (crea matrícula nueva, no reactiva) y desactivar (solo ADMIN).

**Matrículas.** Registrar elige estudiante (sugiere tarifa por edad),
tarifa o concepto flexible o monto libre, beca opcional, diferido y
productos con −1/+1. La pestaña Cuotas muestra el estado de cada cuota.

**Pagos.** Se elige estudiante → cuota pendiente → monto (acepta parciales)
→ método. YAPE/PLIN/TRANSFERENCIA exigen foto de comprobante. La pestaña
Morosos lista las vencidas.

**Ventas y Campeonatos.** Uniforme/Tienda por producto con stock;
Campeonato por división (tarifa) con monto editable, sin producto
obligatorio. La pestaña Campeonatos inscribe estudiantes por división y
muestra recaudado, arbitraje y neto.

**Egresos.** Profesor, Personal, Campeonato fijo, Arbitraje, Viáticos.
Profesor/Arbitraje sugieren el monto por defecto pero **cada caso se edita**.
Comprobante opcional hasta 5MB. Eliminar: solo ADMIN.

**Inventario.** Productos con stock, movimientos de entrada/salida/ajuste
(con motivo e historial), alerta de stock bajo, variantes por talla.

**Tarifas.** Precios de cobro: mensualidades por edad, inscripción,
reingreso, divisiones de campeonato. Pestaña **Becas** para crear
descuentos por porcentaje o monto fijo.

**Reportes.** 6 reportes a Excel (morosos, pagos por fecha, ingresos
mensuales, alumnos por categoría, inventario, becas): elige fechas y carpeta.

**Importar (ADMIN).** Carga masiva desde CSV/Excel con mapeo de columnas y
previsualización.

**Configuración (ADMIN).** Datos de la academia, mora, cuotas y becas,
actualizaciones, respaldos (con Probar conexión y Examinar carpetas),
categorías de edad y campeonato, tipos de uniforme, conceptos flexibles.

**Respaldo.** Botón manual en el menú + automático según frecuencia.
Restaurar pide PIN y exige que las demás PCs cierren el programa.

**Auditoría (ADMIN, solo lectura).** Quién hizo qué y cuándo, con nombre de
usuario; filtros por tabla, usuario y fecha; exporta a Excel.

**Actualizaciones.** Aviso automático con barra de progreso; en Program Files
pide permiso de administrador (normal). Forzar desde Configuración.

## 4. Rutina diaria sugerida

1. Abrir y verificar que entra sin errores (si dice que no hay red, encender la principal).
2. Cobrar y registrar como siempre; ante YAPE pedir comprobante.
3. Fin de jornada: revisar Dashboard (vencidas, neto, stock bajo).
4. Semanal: verificar que existan backups recientes en Configuración.

## 5. Si algo sale mal (resumen)

| Síntoma | Qué hacer |
|---|---|
| No accede a la base de datos | Encender la principal, revisar red y recurso compartido |
| App no reabre | Terminar `AcademiaFutbol.exe` en Administrador de tareas |
| Bloqueo de Windows/antivirus | Ver `guia_instalacion.md` §7 (SmartScreen, exclusión, ZIP) |
| Dato borrado o corrupto | Restaurar backup con PIN (ADMIN, demás PCs cerradas) |
| Olvidó su contraseña | ADMIN la restablece, o PIN de emergencia en el login |

> Flujos detallados con casuísticas: `manual_flujos.md`.
> Matriz de pruebas por release: anexo de `manual_flujos.md`.
