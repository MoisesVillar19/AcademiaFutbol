from database.connection import get_connection, fetch_one
from utils.constants import (
    CATEGORIA_INICIAL,
    CATEGORIA_PRODUCTO_INICIAL,
    DEFAULT_ADMIN_USER,
    DEFAULT_ADMIN_PASS,
    PIN_EMERGENCIA_DEFECTO,
)
from utils.security import hash_password
from utils.dates import get_now


def seed_database() -> None:
    conn = get_connection()
    now = get_now()

    admin_user = fetch_one(
        "SELECT id_usuario FROM usuario WHERE username = ?",
        (DEFAULT_ADMIN_USER,),
    )
    if not admin_user:
        conn.execute(
            """INSERT INTO persona (dni, nombres, apellidos, fecha_creacion)
               VALUES (?, ?, ?, ?)""",
            ("00000000", "Admin", "Sistema", now),
        )
        persona_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        conn.execute(
            """INSERT INTO usuario (id_persona, username, password_hash, rol, fecha_creacion)
               VALUES (?, ?, ?, ?, ?)""",
            (persona_id, DEFAULT_ADMIN_USER, hash_password(DEFAULT_ADMIN_PASS), "ADMIN", now),
        )

    for nombre, edad_min, edad_max in CATEGORIA_INICIAL:
        exists = fetch_one(
            "SELECT id_categoria FROM categoria WHERE nombre = ?",
            (nombre,),
        )
        if not exists:
            conn.execute(
                "INSERT INTO categoria (nombre, edad_min, edad_max) VALUES (?, ?, ?)",
                (nombre, edad_min, edad_max),
            )

    for nombre in CATEGORIA_PRODUCTO_INICIAL:
        exists = fetch_one(
            "SELECT id_categoria_producto FROM categoria_producto WHERE nombre = ?",
            (nombre,),
        )
        if not exists:
            conn.execute(
                "INSERT INTO categoria_producto (nombre) VALUES (?)",
                (nombre,),
            )

    config = fetch_one("SELECT id_configuracion, pin_emergencia FROM configuracion WHERE id_configuracion = 1")
    if not config:
        conn.execute(
            """INSERT INTO configuracion
               (id_configuracion, nombre_academia, dias_por_vencer, permitir_multiples_becas,
                backup_automatico, frecuencia_backup, ruta_backup, pin_emergencia,
                precio_inscripcion, precio_mensualidad, precio_uniforme, precio_reingreso, fecha_actualizacion)
               VALUES (1, 'Academia Deportiva', 3, 1, 1, 7, 'backups/', ?, 100, 100, 20, 100, ?)""",
            (hash_password(PIN_EMERGENCIA_DEFECTO), now),
        )
    elif not config.get("pin_emergencia"):
        conn.execute(
            "UPDATE configuracion SET pin_emergencia = ? WHERE id_configuracion = 1",
            (hash_password(PIN_EMERGENCIA_DEFECTO),),
        )

    # Tipos de uniforme (flexibles, RN-039)
    for nombre, desc in [
        ("Uniforme Entrenamiento", "Camiseta de entrenamiento incluida en inscripción"),
        ("Uniforme Competencia", "Uniforme para competencias"),
        ("Uniforme Completo", "Paquete completo - S/30"),
        ("Uniforme Media", "Media uniforme - S/20"),
    ]:
        exists = fetch_one("SELECT id_tipo_uniforme FROM tipo_uniforme WHERE nombre = ?", (nombre,))
        if not exists:
            conn.execute("INSERT INTO tipo_uniforme (nombre, descripcion) VALUES (?, ?)", (nombre, desc))

    # Tallas escalables (S1)
    for codigo, desc in [("S","Small"),("M","Medium"),("L","Large"),("XL","Extra Large"),("UNICA","Talla única")]:
        exists = fetch_one("SELECT id_talla FROM talla WHERE codigo = ?", (codigo,))
        if not exists:
            conn.execute("INSERT INTO talla (codigo, descripcion) VALUES (?, ?)", (codigo, desc))

    # Almacén y Caja principal (S2, si solo 1 no se muestra)
    exists_alm = fetch_one("SELECT id_almacen FROM almacen WHERE nombre = 'Principal'")
    if not exists_alm:
        conn.execute("INSERT INTO almacen (nombre, direccion) VALUES ('Principal', 'Sede principal')")
        id_alm = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.execute("INSERT INTO caja (id_almacen, nombre, responsable) VALUES (?, 'Caja 1', 'Admin')", (id_alm,))

    # Producto inicial: Camiseta Entrenamiento (RN-036) + stock escalable (incluso si producto ya existe)
    cat_dep = fetch_one("SELECT id_categoria_producto FROM categoria_producto WHERE nombre = 'INSUMO_DEPORTIVO'")
    if cat_dep:
        tipo_ent = fetch_one("SELECT id_tipo_uniforme FROM tipo_uniforme WHERE nombre = 'Uniforme Entrenamiento'")
        exists_prod = fetch_one("SELECT id_producto FROM producto WHERE codigo = 'CAMISETA-ENT'")
        id_prod = None
        if not exists_prod and tipo_ent:
            conn.execute(
                """INSERT INTO producto (id_categoria_producto, tipo_uso, codigo, nombre, stock_actual, stock_minimo, precio, precio_compra, precio_venta, id_tipo_uniforme)
                   VALUES (?, 'VENTA', 'CAMISETA-ENT', 'Camiseta Entrenamiento', 50, 5, 20, 8, 20, ?)""",
                (cat_dep["id_categoria_producto"], tipo_ent["id_tipo_uniforme"]),
            )
            id_prod = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        elif exists_prod:
            id_prod = exists_prod["id_producto"]
        # asegurar variantes y stock_almacen para producto existente (migración)
        if id_prod:
            alm = fetch_one("SELECT id_almacen FROM almacen WHERE nombre='Principal'")
            if alm and not fetch_one("SELECT id_stock FROM stock_almacen WHERE id_producto=? AND id_almacen=? AND id_variante IS NULL", (id_prod, alm["id_almacen"])):
                prod = fetch_one("SELECT stock_actual FROM producto WHERE id_producto=?", (id_prod,))
                stock = prod["stock_actual"] if prod else 50
                conn.execute("INSERT INTO stock_almacen (id_producto, id_almacen, stock) VALUES (?, ?, ?)", (id_prod, alm["id_almacen"], stock))
            for talla_code in ["S","M","L"]:
                t = fetch_one("SELECT id_talla FROM talla WHERE codigo=?", (talla_code,))
                if t:
                    sku = f"CAMISETA-ENT-{talla_code}"
                    if not fetch_one("SELECT id_variante FROM producto_variante WHERE sku=?", (sku,)):
                        conn.execute("INSERT INTO producto_variante (id_producto, id_talla, sku, stock_minimo) VALUES (?, ?, ?, 5)", (id_prod, t["id_talla"], sku))
                        id_var = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                        if alm and not fetch_one("SELECT id_stock FROM stock_almacen WHERE id_variante=?", (id_var,)):
                            conn.execute("INSERT INTO stock_almacen (id_producto, id_variante, id_almacen, stock) VALUES (?, ?, ?, 10)", (id_prod, id_var, alm["id_almacen"]))

    # v2.2: tarifas desde Precios Flexibles (BD nuevas; en existentes lo hace la migración)
    try:
        from database.create_db import seed_tarifas_desde_config
        seed_tarifas_desde_config(conn.cursor())
    except Exception:
        pass

    conn.commit()


if __name__ == "__main__":
    seed_database()
    print("Datos iniciales insertados correctamente.")
