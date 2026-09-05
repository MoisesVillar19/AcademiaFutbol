from repositories import (categoria_producto_repository, producto_repository,
                           movimiento_inventario_repository)
from models.categoria_producto import CategoriaProducto
from models.producto import Producto
from models.movimiento_inventario import MovimientoInventario
from services import auditoria_service
from utils.dates import get_now
from utils.logger import logger


def crear_categoria(data: dict) -> tuple[bool, str, int | None]:
    nombre = data.get("nombre", "")
    if not nombre:
        return False, "El nombre es obligatorio", None

    if categoria_producto_repository.existe_nombre(nombre):
        return False, "Ya existe una categoría con ese nombre", None

    categoria = CategoriaProducto(nombre=nombre)
    id_categoria = categoria_producto_repository.insertar(categoria)

    auditoria_service.registrar_insert(
        id_usuario=1,
        tabla="categoria_producto",
        id_registro=id_categoria,
        valores_nuevos=f"nombre={nombre}",
    )

    logger.info(f"Categoría de producto creada: {nombre}")
    return True, "Categoría creada correctamente", id_categoria


def editar_categoria(id_categoria: int, data: dict) -> tuple[bool, str]:
    categoria = categoria_producto_repository.obtener_por_id(id_categoria)
    if not categoria:
        return False, "Categoría no encontrada"

    nombre = data.get("nombre", categoria["nombre"])
    if categoria_producto_repository.existe_nombre(nombre, exclude_id=id_categoria):
        return False, "Ya existe otra categoría con ese nombre"

    categoria_obj = CategoriaProducto(
        id_categoria_producto=id_categoria,
        nombre=nombre,
        activo=categoria["activo"],
    )
    categoria_producto_repository.actualizar(categoria_obj)

    auditoria_service.registrar_update(
        id_usuario=auditoria_service.id_usuario_sesion(),
        tabla="categoria_producto",
        id_registro=id_categoria,
        valores_anteriores=f"nombre={categoria['nombre']}",
        valores_nuevos=f"nombre={nombre}",
    )

    return True, "Categoría actualizada correctamente"


def listar_categorias(activo: int | None = None) -> list[dict]:
    return categoria_producto_repository.obtener_todas(activo=activo)


def crear_producto(data: dict) -> tuple[bool, str, int | None]:
    codigo = data.get("codigo", "")
    nombre = data.get("nombre", "")
    id_categoria = data.get("id_categoria_producto")

    if not nombre:
        return False, "El nombre es obligatorio", None
    if not id_categoria:
        return False, "La categoría es obligatoria", None

    if not codigo:
        from utils.helpers import generate_product_code
        codigo = generate_product_code()

    if producto_repository.existe_codigo(codigo):
        return False, "Ya existe un producto con ese código", None

    stock_minimo = data.get("stock_minimo", 0)
    try:
        stock_minimo = int(stock_minimo)
    except (ValueError, TypeError):
        stock_minimo = 0

    precio = data.get("precio", 0)
    try:
        precio = float(precio)
    except (ValueError, TypeError):
        precio = 0

    producto = Producto(
        id_categoria_producto=id_categoria,
        tipo_uso=data.get("tipo_uso", "CONSUMO_INTERNO"),
        codigo=codigo,
        nombre=nombre,
        stock_actual=0,
        stock_minimo=stock_minimo,
        precio=precio,
    )
    id_producto = producto_repository.insertar(producto)

    auditoria_service.registrar_insert(
        id_usuario=1,
        tabla="producto",
        id_registro=id_producto,
        valores_nuevos=f"codigo={codigo}, nombre={nombre}",
    )

    logger.info(f"Producto creado: {codigo} - {nombre}")
    return True, "Producto creado correctamente", id_producto


def editar_producto(id_producto: int, data: dict) -> tuple[bool, str]:
    producto = producto_repository.obtener_por_id(id_producto)
    if not producto:
        return False, "Producto no encontrado"

    codigo = data.get("codigo", producto["codigo"])
    if producto_repository.existe_codigo(codigo, exclude_id=id_producto):
        return False, "Ya existe otro producto con ese código"

    stock_minimo = data.get("stock_minimo", producto["stock_minimo"])
    try:
        stock_minimo = int(stock_minimo)
    except (ValueError, TypeError):
        stock_minimo = producto["stock_minimo"]

    precio = data.get("precio", producto["precio"])
    try:
        precio = float(precio)
    except (ValueError, TypeError):
        precio = producto["precio"]

    producto_obj = Producto(
        id_producto=id_producto,
        id_categoria_producto=data.get("id_categoria_producto", producto["id_categoria_producto"]),
        tipo_uso=data.get("tipo_uso", producto["tipo_uso"]),
        codigo=codigo,
        nombre=data.get("nombre", producto["nombre"]),
        stock_actual=producto["stock_actual"],
        stock_minimo=stock_minimo,
        precio=precio,
        activo=producto["activo"],
    )
    producto_repository.actualizar(producto_obj)

    auditoria_service.registrar_update(
        id_usuario=auditoria_service.id_usuario_sesion(),
        tabla="producto",
        id_registro=id_producto,
        valores_anteriores=f"codigo={producto['codigo']}, nombre={producto['nombre']}, precio={producto['precio']}",
        valores_nuevos=f"codigo={codigo}, nombre={producto_obj.nombre}, precio={precio}",
    )

    return True, "Producto actualizado correctamente"


def registrar_movimiento(data: dict) -> tuple[bool, str, int | None]:
    id_producto = data.get("id_producto")
    tipo_movimiento = data.get("tipo_movimiento", "")
    cantidad = data.get("cantidad", 0)

    if not id_producto:
        return False, "El producto es obligatorio", None
    if tipo_movimiento not in ("ENTRADA", "SALIDA", "AJUSTE"):
        return False, "Tipo de movimiento no válido", None
    if cantidad <= 0:
        return False, "La cantidad debe ser mayor a 0", None

    producto = producto_repository.obtener_por_id(id_producto)
    if not producto:
        return False, "Producto no encontrado", None

    stock_anterior = producto["stock_actual"]

    if tipo_movimiento == "ENTRADA":
        stock_nuevo = stock_anterior + cantidad
    elif tipo_movimiento == "SALIDA":
        if cantidad > stock_anterior:
            return False, f"Stock insuficiente. Disponible: {stock_anterior}", None
        stock_nuevo = stock_anterior - cantidad
    else:
        stock_nuevo = cantidad

    producto_repository.actualizar_stock(id_producto, stock_nuevo)

    usuario = data.get("id_usuario", 1)
    movimiento = MovimientoInventario(
        id_producto=id_producto,
        id_usuario=usuario,
        tipo_movimiento=tipo_movimiento,
        cantidad=cantidad,
        stock_anterior=stock_anterior,
        stock_nuevo=stock_nuevo,
        fecha_movimiento=get_now(),
        motivo=data.get("motivo", ""),
    )
    id_movimiento = movimiento_inventario_repository.insertar(movimiento)

    auditoria_service.registrar_insert(
        id_usuario=usuario,
        tabla="movimiento_inventario",
        id_registro=id_movimiento,
        valores_nuevos=f"producto={id_producto}, tipo={tipo_movimiento}, cantidad={cantidad}",
    )

    logger.info(f"Movimiento registrado: {tipo_movimiento} x{cantidad} producto={id_producto}")
    return True, f"Movimiento registrado. Stock: {stock_nuevo}", id_movimiento


def obtener_producto(id_producto: int) -> dict | None:
    return producto_repository.obtener_por_id(id_producto)


def listar_productos(activo: int | None = None) -> list[dict]:
    return producto_repository.obtener_todos(activo=activo)


def obtener_bajo_stock() -> list[dict]:
    return producto_repository.obtener_bajo_stock()


def listar_movimientos(limit: int = 100, offset: int = 0) -> list[dict]:
    return movimiento_inventario_repository.obtener_todos(limit=limit, offset=offset)


def listar_movimientos_por_producto(id_producto: int) -> list[dict]:
    return movimiento_inventario_repository.obtener_por_producto(id_producto)


def listar_movimientos_por_fecha(fecha_inicio: str, fecha_fin: str) -> list[dict]:
    return movimiento_inventario_repository.obtener_por_fecha(fecha_inicio, fecha_fin)
