"""Servicio CRUD para inventario"""
from datetime import date
from db import get_connection


def crear_articulo(nombre, categoria="", cantidad=0, precio=0.0):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO inventario (nombre, categoria, cantidad, precio, fecha_registro)
        VALUES (?, ?, ?, ?, ?)
    """, (nombre, categoria, cantidad, precio, date.today().isoformat()))

    articulo_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return articulo_id


def obtener_articulo(articulo_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM inventario WHERE id = ?", (articulo_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def listar_articulos(buscar="", solo_activos=True):
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM inventario WHERE 1=1"
    params = []

    if solo_activos:
        query += " AND activo = 1"

    if buscar:
        query += " AND (nombre LIKE ? OR categoria LIKE ?)"
        buscar_param = f"%{buscar}%"
        params.extend([buscar_param, buscar_param])

    query += " ORDER BY nombre"

    cursor.execute(query, params)
    articulos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return articulos


def actualizar_articulo(articulo_id, nombre, categoria="", cantidad=0, precio=0.0):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE inventario
        SET nombre = ?, categoria = ?, cantidad = ?, precio = ?
        WHERE id = ?
        """,
        (nombre, categoria, cantidad, precio, articulo_id)
    )

    conn.commit()
    conn.close()


def eliminar_articulo(articulo_id):
    conn = get_connection()
    cursor = conn.cursor()

    # Soft delete
    cursor.execute("UPDATE inventario SET activo = 0 WHERE id = ?", (articulo_id,))

    conn.commit()
    conn.close()
