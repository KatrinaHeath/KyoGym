"""Script para migrar la base de datos existente a la nueva estructura"""
import sqlite3
from pathlib import Path
from utils.constants import DB_PATH

def migrar_base_datos():
    """Migra la base de datos existente agregando los nuevos campos"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        # Verificar si la columna sexo ya existe
        cursor.execute("PRAGMA table_info(clientes)")
        columnas = [col[1] for col in cursor.fetchall()]
        
        cambios_realizados = False
        
        # Agregar columna sexo si no existe
        if 'sexo' not in columnas:
            cursor.execute("ALTER TABLE clientes ADD COLUMN sexo TEXT")
            print("✓ Agregada columna 'sexo' a la tabla clientes")
            cambios_realizados = True
        
        # Agregar columna fecha_nacimiento si no existe
        if 'fecha_nacimiento' not in columnas:
            cursor.execute("ALTER TABLE clientes ADD COLUMN fecha_nacimiento DATE")
            print("✓ Agregada columna 'fecha_nacimiento' a la tabla clientes")
            cambios_realizados = True
        
        # Nota: SQLite no permite eliminar columnas directamente con ALTER TABLE
        # La columna 'cedula' permanecerá en la base de datos pero no se usará
        
        if cambios_realizados:
            conn.commit()
            print("\n✅ Migración completada exitosamente")
        else:
            print("\n✓ La base de datos ya está actualizada")
        
    except Exception as e:
        print(f"\n❌ Error durante la migración: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("Iniciando migración de base de datos...")
    print(f"Base de datos: {DB_PATH}\n")
    migrar_base_datos()
