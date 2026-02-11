"""Servicio CRUD para membresías"""
from datetime import date, timedelta
from db import get_connection
from utils.constants import ESTADO_ACTIVA, ESTADO_POR_VENCER, ESTADO_VENCIDA, DIAS_ALERTA_VENCIMIENTO


def calcular_estado_membresia(fecha_vencimiento_str):
    """Calcula el estado de una membresía según su fecha de vencimiento"""
    fecha_vencimiento = date.fromisoformat(fecha_vencimiento_str)
    hoy = date.today()
    dias_restantes = (fecha_vencimiento - hoy).days
    
    if dias_restantes < 0:
        return ESTADO_VENCIDA
    elif dias_restantes <= DIAS_ALERTA_VENCIMIENTO:
        return ESTADO_POR_VENCER
    else:
        return ESTADO_ACTIVA


def crear_membresia(cliente_id, tipo="Mensual", monto=0.0, fecha_inicio=None, pago_id=None):
    """Crea una nueva membresía para un cliente"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if fecha_inicio is None:
        fecha_inicio = date.today()
    elif isinstance(fecha_inicio, str):
        fecha_inicio = date.fromisoformat(fecha_inicio)
    
    # Calcular fecha de vencimiento (30 días por defecto para mensual)
    fecha_vencimiento = fecha_inicio + timedelta(days=30)
    
    cursor.execute("""
        INSERT INTO membresias (cliente_id, tipo, fecha_inicio, fecha_vencimiento, monto, pago_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (cliente_id, tipo, fecha_inicio.isoformat(), fecha_vencimiento.isoformat(), monto, pago_id))
    
    membresia_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return membresia_id


def obtener_membresia(membresia_id):
    """Obtiene una membresía por ID con información del cliente"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT m.*, c.nombre as cliente_nombre
        FROM membresias m
        JOIN clientes c ON m.cliente_id = c.id
        WHERE m.id = ?
    """, (membresia_id,))
    
    membresia = cursor.fetchone()
    conn.close()
    
    if membresia:
        membresia_dict = dict(membresia)
        membresia_dict['estado'] = calcular_estado_membresia(membresia_dict['fecha_vencimiento'])
        return membresia_dict
    return None


def listar_membresias(cliente_id=None, estado=None):
    """Lista membresías con filtros opcionales"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT m.*, c.nombre as cliente_nombre, c.telefono as cliente_telefono
        FROM membresias m
        JOIN clientes c ON m.cliente_id = c.id
        WHERE c.activo = 1
    """
    params = []
    
    if cliente_id:
        query += " AND m.cliente_id = ?"
        params.append(cliente_id)
    
    query += " ORDER BY m.fecha_vencimiento DESC"
    
    cursor.execute(query, params)
    membresias = []
    
    for row in cursor.fetchall():
        membresia = dict(row)
        membresia['estado'] = calcular_estado_membresia(membresia['fecha_vencimiento'])
        
        # Filtrar por estado si se especifica
        if estado is None or membresia['estado'] == estado:
            membresias.append(membresia)
    
    conn.close()
    return membresias


def obtener_membresia_activa(cliente_id):
    """Obtiene la membresía activa más reciente de un cliente"""
    membresias = listar_membresias(cliente_id=cliente_id)
    
    for membresia in membresias:
        if membresia['estado'] == ESTADO_ACTIVA or membresia['estado'] == ESTADO_POR_VENCER:
            return membresia
    
    return None


def renovar_membresia(cliente_id, monto=0.0):
    """Renueva la membresía de un cliente (crea una nueva desde hoy)"""
    return crear_membresia(cliente_id, tipo="Mensual", monto=monto, fecha_inicio=date.today())


def contar_membresias_por_estado():
    """Cuenta membresías agrupadas por estado"""
    membresias = listar_membresias()
    
    conteo = {
        ESTADO_ACTIVA: 0,
        ESTADO_POR_VENCER: 0,
        ESTADO_VENCIDA: 0
    }
    
    for membresia in membresias:
        conteo[membresia['estado']] += 1
    
    return conteo


def obtener_proximas_a_vencer(limite=10):
    """Obtiene las membresías que están por vencer ordenadas por fecha"""
    membresias = listar_membresias(estado=ESTADO_POR_VENCER)
    
    # Ordenar por fecha de vencimiento ascendente
    membresias.sort(key=lambda x: x['fecha_vencimiento'])
    
    return membresias[:limite]


def actualizar_membresia(membresia_id, cliente_id, tipo, fecha_inicio, monto):
    """Actualiza una membresía existente"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if isinstance(fecha_inicio, str):
        fecha_inicio = date.fromisoformat(fecha_inicio)
    
    # Recalcular fecha de vencimiento
    fecha_vencimiento = fecha_inicio + timedelta(days=30)
    
    cursor.execute("""
        UPDATE membresias
        SET cliente_id = ?, tipo = ?, fecha_inicio = ?, fecha_vencimiento = ?, monto = ?
        WHERE id = ?
    """, (cliente_id, tipo, fecha_inicio.isoformat(), fecha_vencimiento.isoformat(), monto, membresia_id))
    
    conn.commit()
    conn.close()


def eliminar_membresia(membresia_id):
    """Elimina una membresía"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM membresias WHERE id = ?", (membresia_id,))
    
    conn.commit()
    conn.close()

