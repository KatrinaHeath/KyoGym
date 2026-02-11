"""
KyoGym - Sistema de Gestión de Gimnasio
Aplicación de escritorio para Windows
"""
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QStackedWidget, QLabel, QFrame)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QIcon

# Inicializar base de datos
from db import init_database

# Importar vistas
from views.dashboard_view import DashboardView
from views.membresias_view import MembresiasView
from views.clientes_view import ClientesView
from views.pagos_view import PagosView
from views.inventario_view import InventarioView


class SidebarButton(QPushButton):
    """Botón personalizado para el sidebar"""
    def __init__(self, texto, icono=None):
        super().__init__(texto)
        self.setCheckable(True)
        self.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 15px 20px;
                border: none;
                background-color: transparent;
                color: #ecf0f1;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton:checked {
                background-color: #3498db;
                border-left: 4px solid #2980b9;
            }
        """)


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KyoGym - Sistema de Gestión")
        self.setMinimumSize(1200, 700)
        self.resize(1400, 800)  # Tamaño inicial más grande
        
        # Inicializar base de datos
        init_database()
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal (horizontal)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        sidebar = self.crear_sidebar()
        main_layout.addWidget(sidebar)
        
        # Contenedor de vistas
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: #f5f6fa;")
        
        # Agregar vistas
        self.dashboard_view = DashboardView()
        self.membresias_view = MembresiasView()
        self.clientes_view = ClientesView()
        self.pagos_view = PagosView()
        self.inventario_view = InventarioView()
        
        self.stack.addWidget(self.dashboard_view)
        self.stack.addWidget(self.membresias_view)
        self.stack.addWidget(self.clientes_view)
        self.stack.addWidget(self.pagos_view)
        self.stack.addWidget(self.inventario_view)
        
        main_layout.addWidget(self.stack)
        
        # Establecer proporción (sidebar : contenido = 1 : 4)
        main_layout.setStretch(0, 1)
        main_layout.setStretch(1, 4)
        
        # Mostrar dashboard por defecto
        self.btn_inicio.setChecked(True)
        self.stack.setCurrentWidget(self.dashboard_view)
    
    def crear_sidebar(self):
        """Crea el sidebar de navegación"""
        sidebar = QFrame()
        sidebar.setStyleSheet("background-color: #2c3e50;")
        sidebar.setMaximumWidth(250)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Logo/Título
        header = QLabel("KyoGym")
        header.setFont(QFont("Arial", 20, QFont.Bold))
        header.setStyleSheet("""
            background-color: #1a252f;
            color: #3498db;
            padding: 20px;
        """)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Separador
        separador = QFrame()
        separador.setFrameShape(QFrame.HLine)
        separador.setStyleSheet("background-color: #34495e;")
        layout.addWidget(separador)
        
        # Botones de navegación
        self.btn_inicio = SidebarButton("🏠 Inicio")
        self.btn_membresias = SidebarButton("👥 Membresías")
        self.btn_clientes = SidebarButton("👤 Clientes")
        self.btn_pagos = SidebarButton("💰 Pagos")
        self.btn_inventario = SidebarButton("📦 Inventario")
        
        self.btn_inicio.clicked.connect(lambda: self.cambiar_vista(0, self.btn_inicio))
        self.btn_membresias.clicked.connect(lambda: self.cambiar_vista(1, self.btn_membresias))
        self.btn_clientes.clicked.connect(lambda: self.cambiar_vista(2, self.btn_clientes))
        self.btn_pagos.clicked.connect(lambda: self.cambiar_vista(3, self.btn_pagos))
        self.btn_inventario.clicked.connect(lambda: self.cambiar_vista(4, self.btn_inventario))
        
        layout.addWidget(self.btn_inicio)
        layout.addWidget(self.btn_membresias)
        layout.addWidget(self.btn_clientes)
        layout.addWidget(self.btn_pagos)
        layout.addWidget(self.btn_inventario)
        
        # Espacio flexible
        layout.addStretch()
        
        # Configuración (al final)
        btn_config = SidebarButton("⚙️ Configuración")
        btn_config.setEnabled(False)  # Deshabilitado por ahora
        layout.addWidget(btn_config)
        
        return sidebar
    
    def cambiar_vista(self, indice, boton):
        """Cambia la vista actual"""
        # Desmarcar todos los botones
        self.btn_inicio.setChecked(False)
        self.btn_membresias.setChecked(False)
        self.btn_clientes.setChecked(False)
        self.btn_pagos.setChecked(False)
        self.btn_inventario.setChecked(False)
        
        # Marcar el botón actual
        boton.setChecked(True)
        
        # Cambiar vista
        self.stack.setCurrentIndex(indice)
        
        # Recargar datos si es dashboard
        if indice == 0:
            self.dashboard_view.cargar_datos()
        elif indice == 3:
            self.pagos_view.actualizar_total_mes()


def main():
    """Función principal"""
    app = QApplication(sys.argv)
    
    # Configurar estilo global
    app.setStyle("Fusion")
    
    try:
        print("[DEBUG] Creando ventana MainWindow()")
        window = MainWindow()
        print("[DEBUG] Llamando window.show()")
        window.show()
        # Intentos adicionales para asegurar que la ventana quede visible
        window.showNormal()
        app.processEvents()
        print("[DEBUG] Llamando raise_() y activateWindow()")
        window.raise_()
        window.activateWindow()
        # Forzar estado normal y activo
        window.setWindowState((window.windowState() & ~Qt.WindowMinimized) | Qt.WindowActive)
        QTimer.singleShot(150, lambda: (window.raise_(), window.activateWindow()))
        QTimer.singleShot(500, lambda: (window.raise_(), window.activateWindow()))

        print("[DEBUG] Ejecutando app.exec()")
        exit_code = app.exec()
        print(f"[DEBUG] app.exec() finalizó con código: {exit_code}")
        sys.exit(exit_code)
    except Exception as e:
        import traceback
        print("[ERROR] Excepción en main():", e)
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
