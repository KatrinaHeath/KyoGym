"""Servicio CRUD para pagos"""
from datetime import date, datetime
from db import get_connection


def crear_pago(cliente_id, monto, metodo, fecha_pago=None, concepto=""):
    """Registra un nuevo pago"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if fecha_pago is None:
        fecha_pago = date.today()
    elif isinstance(fecha_pago, str):
        fecha_pago = date.fromisoformat(fecha_pago)
    
    cursor.execute("""
        INSERT INTO pagos (cliente_id, fecha, monto, metodo, concepto)
        VALUES (?, ?, ?, ?, ?)
    """, (cliente_id, fecha_pago.isoformat(), monto, metodo, concepto))
    
    pago_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return pago_id


def obtener_pago(pago_id):
    """Obtiene un pago por ID con información del cliente"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT p.*, c.nombre as cliente_nombre
        FROM pagos p
        JOIN clientes c ON p.cliente_id = c.id
        WHERE p.id = ?
    """, (pago_id,))
    
    pago = cursor.fetchone()
    conn.close()
    return dict(pago) if pago else None


def listar_pagos(cliente_id=None, fecha_desde=None, fecha_hasta=None, limite=100):
    """Lista pagos con filtros opcionales"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT p.*, c.nombre as cliente_nombre, c.telefono as cliente_telefono
        FROM pagos p
        JOIN clientes c ON p.cliente_id = c.id
        WHERE 1=1
    """
    params = []
    
    if cliente_id:
        query += " AND p.cliente_id = ?"
        params.append(cliente_id)
    
    if fecha_desde:
        query += " AND p.fecha >= ?"
        params.append(fecha_desde if isinstance(fecha_desde, str) else fecha_desde.isoformat())
    
    if fecha_hasta:
        query += " AND p.fecha <= ?"
        params.append(fecha_hasta if isinstance(fecha_hasta, str) else fecha_hasta.isoformat())
    
    query += " ORDER BY p.fecha DESC, p.id DESC LIMIT ?"
    params.append(limite)
    
    cursor.execute(query, params)
    pagos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return pagos


def obtener_pagos_del_mes(año=None, mes=None):
    """Obtiene todos los pagos del mes actual o del mes especificado"""
    if año is None or mes is None:
        hoy = date.today()
        año = hoy.year
        mes = hoy.month
    
    # Primer día del mes
    fecha_desde = date(año, mes, 1)
    
    # Último día del mes
    if mes == 12:
        fecha_hasta = date(año, 12, 31)
    else:
        fecha_hasta = date(año, mes + 1, 1)
        fecha_hasta = fecha_hasta.replace(day=1)
        from datetime import timedelta
        fecha_hasta = fecha_hasta - timedelta(days=1)
    
    return listar_pagos(fecha_desde=fecha_desde, fecha_hasta=fecha_hasta, limite=1000)


def calcular_total_mes(año=None, mes=None):
    """Calcula el total de pagos del mes"""
    pagos = obtener_pagos_del_mes(año, mes)
    return sum(pago['monto'] for pago in pagos)


def obtener_ultimos_pagos(limite=5):
    """Obtiene los últimos pagos registrados"""
    return listar_pagos(limite=limite)


def obtener_historial_pagos_cliente(cliente_id):
    """Obtiene todo el historial de pagos de un cliente"""
    return listar_pagos(cliente_id=cliente_id, limite=1000)


def actualizar_pago(pago_id, cliente_id, monto, metodo, fecha_pago, concepto=""):
    """Actualiza un pago existente"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if isinstance(fecha_pago, date):
        fecha_pago = fecha_pago.isoformat()
    
    cursor.execute("""
        UPDATE pagos
        SET cliente_id = ?, fecha = ?, monto = ?, metodo = ?, concepto = ?
        WHERE id = ?
    """, (cliente_id, fecha_pago, monto, metodo, concepto, pago_id))
    
    conn.commit()
    conn.close()


def eliminar_pago(pago_id):
    """Elimina un pago"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM pagos WHERE id = ?", (pago_id,))
    
    conn.commit()
    conn.close()

