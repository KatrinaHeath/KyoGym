"""Vista placeholder del inventario"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class InventarioView(QWidget):
    """Vista placeholder para inventario"""
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        titulo = QLabel("Inventario")
        titulo.setFont(QFont("Arial", 24, QFont.Bold))
        layout.addWidget(titulo)
        
        mensaje = QLabel("Módulo en desarrollo")
        mensaje.setFont(QFont("Arial", 16))
        mensaje.setStyleSheet("color: #7f8c8d; margin-top: 50px;")
        mensaje.setAlignment(Qt.AlignCenter)
        layout.addWidget(mensaje)
        
        layout.addStretch()
        
        self.setLayout(layout)
