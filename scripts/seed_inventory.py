import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from services import inventario_service

productos = [
    ("Proteína Whey 2lb Vainilla", "Suplementos", 15, 45.00),
    ("Creatina Monohidratada 300g", "Suplementos", 20, 25.00),
    ("Pre-Entreno Explosivo 30 servicios", "Suplementos", 10, 35.00),
    ("BCAA Aminoácidos 200g", "Suplementos", 12, 30.00),
    ("Multivitamínico Deportivo 90 tabletas", "Suplementos", 18, 20.00),
    ("Quemador de Grasa Termogénico", "Suplementos", 8, 40.00),
    ("Mancuernas Ajustables 20kg", "Equipamiento", 5, 120.00),
    ("Barra Olímpica 20kg", "Equipamiento", 4, 180.00),
    ("Banco Plano de Pesas", "Equipamiento", 3, 150.00),
    ("Set de Discos 50kg", "Equipamiento", 6, 200.00),
    ("Máquina de Poleas (Cable)", "Equipamiento", 2, 900.00),
    ("Kettlebell 16kg", "Equipamiento", 7, 60.00),
    ("Guantes de Entrenamiento Antideslizantes", "Accesorios", 25, 15.00),
    ("Cinturón de Levantamiento de Pesas", "Accesorios", 10, 35.00),
    ("Banda Elástica de Resistencia", "Accesorios", 30, 10.00),
    ("Shaker Mezclador 700ml", "Accesorios", 20, 8.00),
    ("Rodillo de Espuma (Foam Roller)", "Accesorios", 12, 18.00),
    ("Cuerda para Saltar Profesional", "Accesorios", 15, 12.00),
    ("Bebida Isotónica Energética 500ml", "Bebidas", 40, 3.00),
    ("Agua Mineral Premium 1L", "Bebidas", 50, 2.00),
]

inserted = 0
for nombre, categoria, cantidad, precio in productos:
    try:
        inventario_service.crear_producto(nombre=nombre, categoria=categoria, cantidad=cantidad, precio=precio)
        inserted += 1
    except Exception as e:
        print(f"Error inserting {nombre}: {e}")

print(f"Inserted {inserted} products")
