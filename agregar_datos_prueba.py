"""Script para agregar datos de prueba a la base de datos"""
from datetime import date, timedelta
from db import init_database
from services.cliente_service import crear_cliente
from services.membresia_service import crear_membresia
from services.pago_service import crear_pago

def agregar_datos_prueba():
    """Agrega datos de prueba al sistema"""
    print("Inicializando base de datos...")
    init_database()
    
    print("\nCreando clientes de prueba...")
    
    # Cliente 1: Membresía activa
    cliente1 = crear_cliente("Juan Pérez", "6789-0123", "001-234567-8")
    fecha_inicio1 = date.today() - timedelta(days=10)
    membresia1 = crear_membresia(cliente1, "Mensual", 50.0, fecha_inicio1)
    crear_pago(cliente1, 50.0, "Efectivo", fecha_inicio1, membresia1, "Membresía mensual")
    print(f"✓ Juan Pérez - Membresía activa")
    
    # Cliente 2: Membresía por vencer
    cliente2 = crear_cliente("Ana Gómez", "3456-7890", "001-345678-9")
    fecha_inicio2 = date.today() - timedelta(days=25)
    membresia2 = crear_membresia(cliente2, "Mensual", 50.0, fecha_inicio2)
    crear_pago(cliente2, 50.0, "Tarjeta", fecha_inicio2, membresia2, "Pago mensual")
    print(f"✓ Ana Gómez - Membresía por vencer (5 días)")
    
    # Cliente 3: Membresía vencida
    cliente3 = crear_cliente("Carlos Ruiz", "1234-5678", "001-456789-0")
    fecha_inicio3 = date.today() - timedelta(days=35)
    membresia3 = crear_membresia(cliente3, "Mensual", 50.0, fecha_inicio3)
    crear_pago(cliente3, 50.0, "Efectivo", fecha_inicio3, membresia3, "Renovación")
    print(f"✓ Carlos Ruiz - Membresía vencida")
    
    # Cliente 4: Membresía activa
    cliente4 = crear_cliente("Luis Torres", "2345-6789")
    fecha_inicio4 = date.today() - timedelta(days=8)
    membresia4 = crear_membresia(cliente4, "Mensual", 50.0, fecha_inicio4)
    crear_pago(cliente4, 50.0, "Efectivo", fecha_inicio4, membresia4)
    print(f"✓ Luis Torres - Membresía activa")
    
    # Cliente 5: Membresía activa
    cliente5 = crear_cliente("María León", "4567-8901", "001-567890-1")
    fecha_inicio5 = date.today() - timedelta(days=15)
    membresia5 = crear_membresia(cliente5, "Mensual", 40.0, fecha_inicio5)
    crear_pago(cliente5, 40.0, "Tarjeta", fecha_inicio5, membresia5, "Membresía mensual")
    print(f"✓ María León - Membresía activa")
    
    # Cliente 6: Membresía por vencer
    cliente6 = crear_cliente("Pedro Soto", "5678-9012")
    fecha_inicio6 = date.today() - timedelta(days=27)
    membresia6 = crear_membresia(cliente6, "Mensual", 50.0, fecha_inicio6)
    crear_pago(cliente6, 50.0, "Transferencia", fecha_inicio6, membresia6)
    print(f"✓ Pedro Soto - Membresía por vencer (3 días)")
    
    # Agregar algunos pagos adicionales del mes
    crear_pago(cliente1, 50.0, "Efectivo", date.today() - timedelta(days=2), concepto="Pago adicional")
    crear_pago(cliente4, 50.0, "Tarjeta", date.today() - timedelta(days=1), concepto="Renovación adelantada")
    
    print("\n✓ Datos de prueba agregados exitosamente")
    print(f"\nTotal de clientes: 6")
    print(f"Total de membresías: 6")
    print(f"Total de pagos: 8")
    print(f"\nBase de datos ubicada en: AppData/Roaming/GymApp/gimnasio.db")
    print("\nPuedes ejecutar 'python main.py' para ver la aplicación")

if __name__ == "__main__":
    agregar_datos_prueba()
