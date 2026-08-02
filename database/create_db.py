from database.connection import get_connection


TABLES_SQL = """
CREATE TABLE IF NOT EXISTS persona (
    id_persona INTEGER PRIMARY KEY AUTOINCREMENT,
    dni TEXT UNIQUE NOT NULL,
    nombres TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    fecha_nacimiento TEXT,
    sexo TEXT CHECK(sexo IN ('M', 'F')),
    direccion TEXT,
    telefono TEXT,
    correo TEXT,
    activo INTEGER DEFAULT 1,
    fecha_creacion TEXT NOT NULL,
    fecha_actualizacion TEXT
);

CREATE TABLE IF NOT EXISTS usuario (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    id_persona INTEGER UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    rol TEXT NOT NULL CHECK(rol IN ('ADMIN', 'SECRETARIA')),
    activo INTEGER DEFAULT 1,
    fecha_creacion TEXT NOT NULL,
    fecha_actualizacion TEXT,
    FOREIGN KEY (id_persona) REFERENCES persona(id_persona)
);

CREATE TABLE IF NOT EXISTS apoderado (
    id_apoderado INTEGER PRIMARY KEY AUTOINCREMENT,
    id_persona INTEGER UNIQUE NOT NULL,
    parentesco TEXT,
    ocupacion TEXT,
    activo INTEGER DEFAULT 1,
    fecha_creacion TEXT NOT NULL,
    fecha_actualizacion TEXT,
    FOREIGN KEY (id_persona) REFERENCES persona(id_persona)
);

CREATE TABLE IF NOT EXISTS estudiante (
    id_estudiante INTEGER PRIMARY KEY AUTOINCREMENT,
    id_persona INTEGER UNIQUE NOT NULL,
    estado TEXT NOT NULL DEFAULT 'ACTIVO' CHECK(estado IN ('ACTIVO', 'RETIRADO', 'REINGRESANTE')),
    fecha_ingreso TEXT NOT NULL,
    fecha_retiro TEXT,
    activo INTEGER DEFAULT 1,
    FOREIGN KEY (id_persona) REFERENCES persona(id_persona)
);

CREATE TABLE IF NOT EXISTS estudiante_apoderado (
    id_estudiante_apoderado INTEGER PRIMARY KEY AUTOINCREMENT,
    id_estudiante INTEGER NOT NULL,
    id_apoderado INTEGER NOT NULL,
    es_principal INTEGER DEFAULT 0,
    activo INTEGER DEFAULT 1,
    FOREIGN KEY (id_estudiante) REFERENCES estudiante(id_estudiante),
    FOREIGN KEY (id_apoderado) REFERENCES apoderado(id_apoderado)
);

CREATE TABLE IF NOT EXISTS categoria (
    id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL,
    edad_min INTEGER NOT NULL,
    edad_max INTEGER NOT NULL,
    activo INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS tarifa (
    id_tarifa INTEGER PRIMARY KEY AUTOINCREMENT,
    id_categoria INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    monto REAL NOT NULL,
    descripcion TEXT,
    fecha_inicio TEXT NOT NULL,
    fecha_fin TEXT,
    observaciones TEXT,
    activo INTEGER DEFAULT 1,
    FOREIGN KEY (id_categoria) REFERENCES categoria(id_categoria)
);

CREATE TABLE IF NOT EXISTS beca (
    id_beca INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK(tipo IN ('PORCENTAJE', 'MONTO_FIJO')),
    valor REAL NOT NULL,
    observacion TEXT,
    activo INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS matricula (
    id_matricula INTEGER PRIMARY KEY AUTOINCREMENT,
    id_estudiante INTEGER NOT NULL,
    id_tarifa INTEGER NOT NULL,
    monto_pactado REAL,
    fecha_inicio TEXT NOT NULL,
    fecha_fin TEXT,
    dia_vencimiento INTEGER NOT NULL DEFAULT 1 CHECK(dia_vencimiento BETWEEN 1 AND 31),
    estado TEXT NOT NULL DEFAULT 'ACTIVO',
    activo INTEGER DEFAULT 1,
    FOREIGN KEY (id_estudiante) REFERENCES estudiante(id_estudiante),
    FOREIGN KEY (id_tarifa) REFERENCES tarifa(id_tarifa)
);

CREATE TABLE IF NOT EXISTS matricula_beca (
    id_matricula_beca INTEGER PRIMARY KEY AUTOINCREMENT,
    id_matricula INTEGER NOT NULL,
    id_beca INTEGER NOT NULL,
    fecha_asignacion TEXT NOT NULL,
    activo INTEGER DEFAULT 1,
    observacion TEXT,
    FOREIGN KEY (id_matricula) REFERENCES matricula(id_matricula),
    FOREIGN KEY (id_beca) REFERENCES beca(id_beca)
);

CREATE TABLE IF NOT EXISTS cuota (
    id_cuota INTEGER PRIMARY KEY AUTOINCREMENT,
    id_matricula INTEGER NOT NULL,
    periodo TEXT NOT NULL,
    fecha_vencimiento TEXT NOT NULL,
    monto_total REAL NOT NULL,
    monto_pagado REAL DEFAULT 0,
    saldo REAL NOT NULL,
    estado TEXT NOT NULL DEFAULT 'PENDIENTE' CHECK(estado IN ('PENDIENTE', 'PARCIAL', 'PAGADO', 'VENCIDO')),
    activo INTEGER DEFAULT 1,
    FOREIGN KEY (id_matricula) REFERENCES matricula(id_matricula)
);

CREATE TABLE IF NOT EXISTS pago (
    id_pago INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    numero_recibo TEXT UNIQUE NOT NULL,
    fecha_pago TEXT NOT NULL,
    monto_total REAL NOT NULL,
    metodo_pago TEXT NOT NULL CHECK(metodo_pago IN ('EFECTIVO', 'YAPE', 'PLIN', 'TRANSFERENCIA')),
    observacion TEXT,
    activo INTEGER DEFAULT 1,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
);

CREATE TABLE IF NOT EXISTS detalle_pago (
    id_detalle_pago INTEGER PRIMARY KEY AUTOINCREMENT,
    id_pago INTEGER NOT NULL,
    id_cuota INTEGER NOT NULL,
    monto_pagado REAL NOT NULL,
    FOREIGN KEY (id_pago) REFERENCES pago(id_pago),
    FOREIGN KEY (id_cuota) REFERENCES cuota(id_cuota)
);

CREATE TABLE IF NOT EXISTS categoria_producto (
    id_categoria_producto INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL,
    activo INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS producto (
    id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
    id_categoria_producto INTEGER NOT NULL,
    tipo_uso TEXT NOT NULL CHECK(tipo_uso IN ('CONSUMO_INTERNO', 'VENTA')),
    codigo TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    stock_actual INTEGER DEFAULT 0,
    stock_minimo INTEGER DEFAULT 0,
    precio REAL DEFAULT 0,
    activo INTEGER DEFAULT 1,
    FOREIGN KEY (id_categoria_producto) REFERENCES categoria_producto(id_categoria_producto)
);

CREATE TABLE IF NOT EXISTS movimiento_inventario (
    id_movimiento INTEGER PRIMARY KEY AUTOINCREMENT,
    id_producto INTEGER NOT NULL,
    id_usuario INTEGER NOT NULL,
    tipo_movimiento TEXT NOT NULL CHECK(tipo_movimiento IN ('ENTRADA', 'SALIDA', 'AJUSTE')),
    cantidad INTEGER NOT NULL,
    stock_anterior INTEGER NOT NULL,
    stock_nuevo INTEGER NOT NULL,
    fecha_movimiento TEXT NOT NULL,
    motivo TEXT,
    FOREIGN KEY (id_producto) REFERENCES producto(id_producto),
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
);

CREATE TABLE IF NOT EXISTS configuracion (
    id_configuracion INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_academia TEXT,
    direccion TEXT,
    telefono TEXT,
    correo TEXT,
    mora_habilitada INTEGER DEFAULT 0,
    porcentaje_mora REAL DEFAULT 0,
    dias_por_vencer INTEGER DEFAULT 3,
    permitir_multiples_becas INTEGER DEFAULT 1,
    backup_automatico INTEGER DEFAULT 1,
    frecuencia_backup INTEGER DEFAULT 7,
    ruta_backup TEXT DEFAULT 'backups/',
    correo_onedrive TEXT DEFAULT '',
    fecha_actualizacion TEXT
);

CREATE TABLE IF NOT EXISTS log (
    id_log INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    tabla_afectada TEXT NOT NULL,
    id_registro INTEGER NOT NULL,
    accion TEXT NOT NULL,
    valor_anterior TEXT,
    valor_nuevo TEXT,
    fecha TEXT NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
);
"""

INDEXES_SQL = """
CREATE INDEX IF NOT EXISTS idx_persona_dni ON persona(dni);
CREATE INDEX IF NOT EXISTS idx_usuario_username ON usuario(username);
CREATE INDEX IF NOT EXISTS idx_cuota_estado ON cuota(estado);
CREATE INDEX IF NOT EXISTS idx_cuota_vencimiento ON cuota(fecha_vencimiento);
CREATE INDEX IF NOT EXISTS idx_pago_fecha ON pago(fecha_pago);
CREATE INDEX IF NOT EXISTS idx_producto_codigo ON producto(codigo);
CREATE INDEX IF NOT EXISTS idx_estudiante_apoderado_estudiante ON estudiante_apoderado(id_estudiante);
CREATE INDEX IF NOT EXISTS idx_matricula_beca_matricula ON matricula_beca(id_matricula);
CREATE INDEX IF NOT EXISTS idx_producto_categoria ON producto(id_categoria_producto);
CREATE INDEX IF NOT EXISTS idx_movimiento_producto ON movimiento_inventario(id_producto);
"""


def create_tables() -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript(TABLES_SQL)
    cursor.executescript(INDEXES_SQL)
    conn.commit()


if __name__ == "__main__":
    create_tables()
    print("Tablas creadas correctamente.")
