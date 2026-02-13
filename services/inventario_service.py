"""Servicio CRUD para inventario"""
from datetime import date
from db import get_connection


def crear_producto(nombre, categoria, cantidad=0, precio=0.0):
    """Crea un nuevo producto en el inventario"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO inventario (nombre, categoria, cantidad, precio, fecha_registro)
        VALUES (?, ?, ?, ?, ?)
    """, (nombre, categoria, cantidad, precio, date.today().isoformat()))
    
    producto_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return producto_id


def obtener_producto(producto_id):
    """Obtiene un producto por ID"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM inventario WHERE id = ?
    """, (producto_id,))
    
    producto = cursor.fetchone()
    conn.close()
    return dict(producto) if producto else None


def listar_productos(buscar="", categoria=None):
    """Lista todos los productos con opción de búsqueda y filtro por categoría"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM inventario WHERE 1=1"
    params = []
    
    if buscar:
        query += " AND nombre LIKE ?"
        params.append(f"%{buscar}%")
    
    if categoria:
        query += " AND categoria = ?"
        params.append(categoria)
    
    query += " ORDER BY nombre ASC"
    
    cursor.execute(query, params)
    productos = cursor.fetchall()
    conn.close()
    
    return [dict(producto) for producto in productos]


def actualizar_producto(producto_id, nombre, categoria, cantidad, precio):
    """Actualiza un producto existente"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE inventario
        SET nombre = ?, categoria = ?, cantidad = ?, precio = ?
        WHERE id = ?
    """, (nombre, categoria, cantidad, precio, producto_id))
    
    conn.commit()
    conn.close()


def eliminar_producto(producto_id):
    """Elimina un producto"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM inventario WHERE id = ?", (producto_id,))
    
    conn.commit()
    conn.close()


def actualizar_cantidad(producto_id, cantidad):
    """Actualiza solo la cantidad de un producto"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE inventario
        SET cantidad = ?
        WHERE id = ?
    """, (cantidad, producto_id))
    
    conn.commit()
    conn.close()


def obtener_categorias():
    """Obtiene todas las categorías únicas del inventario"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT DISTINCT categoria FROM inventario
        ORDER BY categoria ASC
    """)
    
    categorias = cursor.fetchall()
    conn.close()
    
    return [cat['categoria'] for cat in categorias]


def contar_productos():
    """Cuenta el total de productos en inventario"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as total FROM inventario")
    resultado = cursor.fetchone()
    conn.close()
    
    return resultado['total'] if resultado else 0


def calcular_valor_total():
    """Calcula el valor total del inventario (cantidad * precio)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT SUM(cantidad * precio) as valor_total 
        FROM inventario
    """)
    
    resultado = cursor.fetchone()
    conn.close()
    
    return resultado['valor_total'] if resultado and resultado['valor_total'] else 0.0


def productos_bajo_stock(minimo=5):
    """Lista productos con stock bajo el mínimo especificado"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM inventario 
        WHERE cantidad < ?
        ORDER BY cantidad ASC
    """, (minimo,))
    
    productos = cursor.fetchall()
    conn.close()
    
    return [dict(producto) for producto in productos]

def vender_producto(producto_id, cantidad, motivo="Venta de producto"):
    """Descuenta inventario y registra movimiento automáticamente"""
    conn = get_connection()
    cursor = conn.cursor()

    # Obtener stock actual
    cursor.execute("SELECT cantidad FROM inventario WHERE id = ?", (producto_id,))
    producto = cursor.fetchone()

    if not producto:
        conn.close()
        return False, "Producto no existe"

    stock_actual = producto["cantidad"]

    if stock_actual < cantidad:
        conn.close()
        return False, "Stock insuficiente"

    # Descontar inventario
    nuevo_stock = stock_actual - cantidad
    cursor.execute("""
        UPDATE inventario
        SET cantidad = ?
        WHERE id = ?
    """, (nuevo_stock, producto_id))

    # Registrar movimiento en historial
    cursor.execute("""
        INSERT INTO inventario_movimientos (producto_id, tipo, cantidad, motivo)
        VALUES (?, 'SALIDA', ?, ?)
    """, (producto_id, cantidad, motivo))

    conn.commit()
    conn.close()

    return True, "Venta registrada correctamente"

def agregar_stock(producto_id, cantidad, motivo="Ingreso de stock"):
    """Aumenta inventario y registra movimiento"""
    conn = get_connection()
    cursor = conn.cursor()

    # Aumentar inventario
    cursor.execute("""
        UPDATE inventario
        SET cantidad = cantidad + ?
        WHERE id = ?
    """, (cantidad, producto_id))

    # Registrar movimiento
    cursor.execute("""
        INSERT INTO inventario_movimientos (producto_id, tipo, cantidad, motivo)
        VALUES (?, 'ENTRADA', ?, ?)
    """, (producto_id, cantidad, motivo))

    conn.commit()
    conn.close()

def obtener_stock_bajo():
    from db import get_connection
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nombre, cantidad, stock_minimo
        FROM inventario
        WHERE cantidad <= stock_minimo
    """)

    productos = cursor.fetchall()
    conn.close()
    return productos

