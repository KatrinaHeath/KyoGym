"""Script de prueba rápida para verificar imports"""
try:
    print("Probando imports...")
    
    from PySide6.QtWidgets import QApplication
    print("✓ PySide6.QtWidgets")
    
    from PySide6.QtCore import Qt
    print("✓ PySide6.QtCore")
    
    from PySide6.QtGui import QPainter, QColor
    print("✓ PySide6.QtGui")
    
    import db
    print("✓ db module")
    
    from services import cliente_service, membresia_service, pago_service
    print("✓ services modules")
    
    from views.dashboard_view import DashboardView
    print("✓ dashboard_view")
    
    print("\n✓ Todos los imports funcionan correctamente!")
    print("\nPuedes ejecutar: python main.py")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
