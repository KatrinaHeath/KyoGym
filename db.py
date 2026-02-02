"""Gestión de base de datos SQLite"""
import sqlite3
from utils.constants import DB_PATH


def get_connection():
    """Obtiene una conexión a la base de datos"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
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
            FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
        )
    """)
    
    # Tabla de pagos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pagos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            membresia_id INTEGER,
            fecha DATE NOT NULL,
            monto REAL NOT NULL,
            metodo TEXT NOT NULL,
            concepto TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
            FOREIGN KEY (membresia_id) REFERENCES membresias(id) ON DELETE SET NULL
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
    
    conn.commit()
    conn.close()
    
    print(f"Base de datos inicializada en: {DB_PATH}")


if __name__ == "__main__":
    init_database()
