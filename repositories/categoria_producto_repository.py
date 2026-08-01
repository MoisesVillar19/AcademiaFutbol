from database.connection import get_connection, fetch_one, fetch_all
from models.categoria_producto import CategoriaProducto


def insertar(categoria: CategoriaProducto) -> int:
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO categoria_producto (nombre, activo) VALUES (?, ?)",
        (categoria.nombre, categoria.activo),
    )
    conn.commit()
    return cursor.lastrowid


def obtener_por_id(id_categoria_producto: int) -> dict | None:
    return fetch_one(
        "SELECT * FROM categoria_producto WHERE id_categoria_producto = ?",
        (id_categoria_producto,),
    )


def obtener_todas(activo: int | None = None) -> list[dict]:
    if activo is not None:
        return fetch_all(
            "SELECT * FROM categoria_producto WHERE activo = ?",
            (activo,),
        )
    return fetch_all("SELECT * FROM categoria_producto")


def existe_nombre(nombre: str, exclude_id: int | None = None) -> bool:
    if exclude_id:
        row = fetch_one(
            "SELECT id_categoria_producto FROM categoria_producto WHERE nombre = ? AND id_categoria_producto != ?",
            (nombre, exclude_id),
        )
    else:
        row = fetch_one(
            "SELECT id_categoria_producto FROM categoria_producto WHERE nombre = ?",
            (nombre,),
        )
    return row is not None


def actualizar(categoria: CategoriaProducto) -> None:
    conn = get_connection()
    conn.execute(
        "UPDATE categoria_producto SET nombre = ?, activo = ? WHERE id_categoria_producto = ?",
        (categoria.nombre, categoria.activo, categoria.id_categoria_producto),
    )
    conn.commit()


def soft_delete(id_categoria_producto: int) -> None:
    conn = get_connection()
    conn.execute(
        "UPDATE categoria_producto SET activo = 0 WHERE id_categoria_producto = ?",
        (id_categoria_producto,),
    )
    conn.commit()
