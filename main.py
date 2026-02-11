"""
KyoGym - Sistema de Gestión de Gimnasio
Aplicación de escritorio para Windows
"""
import sys
import os
import ctypes
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QStackedWidget, QLabel, QFrame,
                               QDialog, QRadioButton, QButtonGroup, QDialogButtonBox, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon, QPixmap

# Inicializar base de datos
from db import init_database
from usuario_activo import obtener_usuario_activo, guardar_usuario_activo, USUARIOS

# Importar vistas
from views.dashboard_view import DashboardView
from views.membresias_view import MembresiasView
from views.clientes_view import ClientesView
from views.pagos_view import PagosView
from views.inventario_view import InventarioView
from views.configuracion_view import ConfiguracionView


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


class CambiarUsuarioDialog(QDialog):
    """Diálogo para cambiar de usuario"""
    def __init__(self, usuario_actual, parent=None):
        super().__init__(parent)
        self.usuario_actual = usuario_actual
        self.setWindowTitle("Cambiar Usuario")
        self.setMinimumWidth(350)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Estilos
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #2c3e50;
                font-size: 13px;
            }
            QRadioButton {
                color: #2c3e50;
                font-size: 13px;
                padding: 10px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        
        # Título
        titulo = QLabel("Seleccione el usuario activo:")
        titulo.setFont(QFont("Arial", 12, QFont.Bold))
        titulo.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(titulo)
        
        # Grupo de radio buttons
        self.grupo_usuarios = QButtonGroup()
        
        for i, usuario in enumerate(USUARIOS):
            radio = QRadioButton(f"👤 {usuario}")
            radio.setStyleSheet("""
                QRadioButton {
                    padding: 10px;
                    font-size: 14px;
                }
                QRadioButton:hover {
                    background-color: #f0f0f0;
                    border-radius: 5px;
                }
            """)
            if usuario == self.usuario_actual:
                radio.setChecked(True)
            self.grupo_usuarios.addButton(radio, i)
            layout.addWidget(radio)
        
        # Espacio
        layout.addSpacing(20)
        
        # Botones
        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botones.accepted.connect(self.accept)
        botones.rejected.connect(self.reject)
        botones.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 20px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 13px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        layout.addWidget(botones)
        
        self.setLayout(layout)
    
    def obtener_usuario_seleccionado(self):
        """Retorna el usuario seleccionado"""
        boton_seleccionado = self.grupo_usuarios.checkedButton()
        if boton_seleccionado:
            id_seleccionado = self.grupo_usuarios.id(boton_seleccionado)
            return USUARIOS[id_seleccionado]
        return None


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KyoGym - Sistema de Gestión")
        self.setMinimumSize(1200, 700)
        self.resize(1400, 800)  # Tamaño inicial más grande
        
        # Establecer icono de la ventana
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))
        
        # Inicializar usuario activo
        self.usuario_activo = obtener_usuario_activo()
        
        # Inicializar base de datos
        init_database()
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        try:
            # Widget central
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Layout principal (horizontal)
            main_layout = QHBoxLayout(central_widget)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            
            # Sidebar (se crea primero para tener los botones disponibles)
            sidebar = self.crear_sidebar()
            main_layout.addWidget(sidebar)
            
            # Contenedor de vistas
            self.stack = QStackedWidget()
            self.stack.setStyleSheet("background-color: #f5f6fa;")
            
            # Agregar vistas
            print("Creando dashboard...")
            self.dashboard_view = DashboardView()
            print("Creando membresías...")
            self.membresias_view = MembresiasView()
            print("Creando clientes...")
            self.clientes_view = ClientesView()
            print("Creando pagos...")
            self.pagos_view = PagosView()
            print("Creando inventario...")
            self.inventario_view = InventarioView()
            print("Creando configuración...")
            self.configuracion_view = ConfiguracionView()
            
            self.stack.addWidget(self.dashboard_view)
            self.stack.addWidget(self.membresias_view)
            self.stack.addWidget(self.clientes_view)
            self.stack.addWidget(self.pagos_view)
            self.stack.addWidget(self.inventario_view)
            self.stack.addWidget(self.configuracion_view)
            
            main_layout.addWidget(self.stack)
            
            # Establecer proporción (sidebar : contenido = 1 : 4)
            main_layout.setStretch(0, 1)
            main_layout.setStretch(1, 4)
            
            # Mostrar dashboard por defecto (ahora btn_inicio ya existe)
            self.btn_inicio.setChecked(True)
            self.stack.setCurrentWidget(self.dashboard_view)
            print("UI inicializada correctamente")
        except Exception as e:
            print(f"Error al inicializar UI: {e}")
            import traceback
            traceback.print_exc()
    
    def crear_sidebar(self):
        """Crea el sidebar de navegación"""
        sidebar = QFrame()
        sidebar.setStyleSheet("background-color: #2c3e50;")
        sidebar.setMaximumWidth(250)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Logo/Título
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: #1a252f;")
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 20, 20, 10)
        header_layout.setSpacing(5)
        
        # Logo
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            # Escalar el logo a 80x80 píxeles manteniendo la proporción
            scaled_pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            header_layout.addWidget(logo_label)
        
        # Título
        titulo = QLabel("KyoGym")
        titulo.setFont(QFont("Arial", 18, QFont.Bold))
        titulo.setStyleSheet("color: #3498db; background-color: transparent;")
        titulo.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(titulo)
        
        layout.addWidget(header_widget)
        
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
        
        # Widget de perfil de usuario
        perfil_widget = self.crear_widget_perfil()
        layout.addWidget(perfil_widget)
        
        # Separador antes de configuración
        separador2 = QFrame()
        separador2.setFrameShape(QFrame.HLine)
        separador2.setStyleSheet("background-color: #34495e;")
        layout.addWidget(separador2)
        
        # Botón de configuración al final
        self.btn_configuracion = SidebarButton("⚙️ Configuración")
        self.btn_configuracion.clicked.connect(lambda: self.cambiar_vista(5, self.btn_configuracion))
        layout.addWidget(self.btn_configuracion)
        
        return sidebar
    
    def crear_widget_perfil(self):
        """Crea el widget de perfil de usuario"""
        perfil_frame = QFrame()
        perfil_frame.setStyleSheet("""
            QFrame {
                background-color: #1a252f;
                border-radius: 5px;
                padding: 10px;
            }
            QFrame:hover {
                background-color: #34495e;
            }
        """)
        perfil_frame.setCursor(Qt.PointingHandCursor)
        
        perfil_layout = QHBoxLayout(perfil_frame)
        perfil_layout.setContentsMargins(10, 10, 10, 10)
        perfil_layout.setSpacing(10)
        
        # Icono de perfil
        icono_label = QLabel("👤")
        icono_label.setStyleSheet("font-size: 24px; background-color: transparent;")
        perfil_layout.addWidget(icono_label)
        
        # Nombre del usuario
        self.nombre_usuario_label = QLabel(self.usuario_activo)
        self.nombre_usuario_label.setStyleSheet("""
            color: #ecf0f1;
            font-size: 13px;
            font-weight: bold;
            background-color: transparent;
        """)
        self.nombre_usuario_label.setWordWrap(True)
        perfil_layout.addWidget(self.nombre_usuario_label, 1)
        
        # Hacer clickeable
        perfil_frame.mousePressEvent = lambda event: self.mostrar_dialogo_cambiar_usuario()
        
        return perfil_frame
    
    def mostrar_dialogo_cambiar_usuario(self):
        """Muestra diálogo para cambiar de usuario"""
        dialog = CambiarUsuarioDialog(self.usuario_activo, self)
        if dialog.exec():
            nuevo_usuario = dialog.obtener_usuario_seleccionado()
            if nuevo_usuario and nuevo_usuario != self.usuario_activo:
                self.usuario_activo = nuevo_usuario
                guardar_usuario_activo(nuevo_usuario)
                self.nombre_usuario_label.setText(nuevo_usuario)
                
                # Mensaje de confirmación
                msg = QMessageBox(self)
                msg.setWindowTitle("Usuario Cambiado")
                msg.setText(f"Usuario activo: {nuevo_usuario}")
                msg.setStyleSheet("""
                    QMessageBox {
                        background-color: white;
                    }
                    QLabel {
                        color: black;
                        font-size: 13px;
                        min-width: 300px;
                    }
                    QPushButton {
                        background-color: #27ae60;
                        color: white;
                        padding: 8px 20px;
                        border: none;
                        border-radius: 4px;
                        font-weight: bold;
                        font-size: 13px;
                        min-width: 80px;
                    }
                    QPushButton:hover {
                        background-color: #229954;
                    }
                """)
                msg.exec()
    
    def cambiar_vista(self, indice, boton):
        """Cambia la vista actual"""
        # Desmarcar todos los botones
        self.btn_inicio.setChecked(False)
        self.btn_membresias.setChecked(False)
        self.btn_clientes.setChecked(False)
        self.btn_pagos.setChecked(False)
        self.btn_inventario.setChecked(False)
        self.btn_configuracion.setChecked(False)
        
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
    # Configurar AppUserModelID para Windows (hace que el icono aparezca en la barra de tareas)
    if sys.platform == 'win32':
        myappid = 'kyogym.gimnasio.app.1.0'  # ID único de tu aplicación
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    
    app = QApplication(sys.argv)
    
    # Establecer icono de la aplicación
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
    if os.path.exists(logo_path):
        app.setWindowIcon(QIcon(logo_path))
    
    # Configurar estilo global
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
