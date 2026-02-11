"""Gestión de base de datos SQLite"""
import sqlite3
from utils.constants import DB_PATH


def get_connection():
    """Obtiene una conexión a la base de datos"""
    conn = sqlite3.connect(str(DB_PATH), timeout=30.0)
    conn.row_factory = sqlite3.Row
    # Habilitar WAL mode para mejor concurrencia
    conn.execute('PRAGMA journal_mode=WAL')
    return conn


def init_database():
    """Inicializa la base de datos y crea las tablas si no existen"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabla de clientes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT,
            sexo TEXT,
            fecha_nacimiento DATE,
            fecha_registro DATE NOT NULL,
            activo INTEGER DEFAULT 1
        )
    """)
    
    # Tabla de membresías
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS membresias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            fecha_inicio DATE NOT NULL,
            fecha_vencimiento DATE NOT NULL,
            monto REAL NOT NULL,
            pago_id INTEGER,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
            FOREIGN KEY (pago_id) REFERENCES pagos(id) ON DELETE SET NULL
        )
    """)
    
    # Tabla de pagos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pagos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            fecha DATE NOT NULL,
            monto REAL NOT NULL,
            metodo TEXT NOT NULL,
            concepto TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
        )
    """)
    
    # Crear índices para mejorar el rendimiento
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_membresias_cliente 
        ON membresias(cliente_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_membresias_vencimiento 
        ON membresias(fecha_vencimiento)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_pagos_cliente 
        ON pagos(cliente_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_pagos_fecha 
        ON pagos(fecha)
    """)
    
    # Tabla de inventario
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            cantidad INTEGER NOT NULL DEFAULT 0,
            precio REAL DEFAULT 0.0,
            fecha_registro DATE DEFAULT (DATE('now'))
        )
    """)
    
    # Índice para búsquedas rápidas por nombre
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_inventario_nombre 
        ON inventario(nombre)
    """)
    
    # Índice para búsquedas por categoría
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_inventario_categoria 
        ON inventario(categoria)
    """)
    
    conn.commit()
    conn.close()
    
    print(f"Base de datos inicializada en: {DB_PATH}")


if __name__ == "__main__":
    init_database()
