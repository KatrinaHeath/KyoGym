"""Vista de gestión de membresías"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QTableWidget, QTableWidgetItem, QHeaderView, QLabel,
                               QDialog, QFormLayout, QLineEdit, QDateEdit, QComboBox,
                               QMessageBox, QDialogButtonBox)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor
from datetime import date
from services import membresia_service, cliente_service
from utils.constants import ESTADO_ACTIVA, ESTADO_POR_VENCER, ESTADO_VENCIDA
from utils.factura_generator import generar_factura_membresia, abrir_factura


class AgregarMembresiaDialog(QDialog):
    """Diálogo para agregar nueva membresía"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nueva Membresía")
        self.setMinimumWidth(400)
        self.init_ui()
    
    def init_ui(self):
        layout = QFormLayout()
        
        # Estilos para el diálogo
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: #2c3e50;
                font-size: 13px;
            }
            QLineEdit, QComboBox, QDateEdit {
                padding: 8px;
                border: 2px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
                color: #2c3e50;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        
        # Selector de cliente
        self.combo_cliente = QComboBox()
        self.cargar_clientes()
        layout.addRow("Cliente:", self.combo_cliente)
        
        # Fecha de inicio
        self.fecha_inicio = QDateEdit()
        self.fecha_inicio.setDate(QDate.currentDate())
        self.fecha_inicio.setCalendarPopup(True)
        layout.addRow("Fecha Inicio:", self.fecha_inicio)
        
        # Monto
        self.monto = QLineEdit()
        self.monto.setPlaceholderText("0.00")
        layout.addRow("Monto:", self.monto)
        
        # Botones
        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botones.accepted.connect(self.aceptar)
        botones.rejected.connect(self.reject)
        layout.addRow(botones)
        
        self.setLayout(layout)
    
    def cargar_clientes(self):
        """Carga la lista de clientes"""
        clientes = cliente_service.listar_clientes()
        self.combo_cliente.clear()
        
        for cliente in clientes:
            self.combo_cliente.addItem(cliente['nombre'], cliente['id'])
    
    def aceptar(self):
        """Valida y acepta el diálogo"""
        if self.combo_cliente.currentData() is None:
            QMessageBox.warning(self, "Error", "Seleccione un cliente")
            return
        
        try:
            float(self.monto.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Ingrese un monto válido")
            return
        
        self.accept()
    
    def obtener_datos(self):
        """Retorna los datos ingresados"""
        fecha = self.fecha_inicio.date()
        return {
            'cliente_id': self.combo_cliente.currentData(),
            'fecha_inicio': date(fecha.year(), fecha.month(), fecha.day()),
            'monto': float(self.monto.text())
        }


class MembresiasView(QWidget):
    """Vista de gestión de membresías"""
    def __init__(self):
        super().__init__()
        self.filtro_actual = "Todos"
        self.init_ui()
        self.cargar_datos()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Encabezado
        header_layout = QHBoxLayout()
        
        titulo = QLabel("Membresías")
        titulo.setFont(QFont("Arial", 24, QFont.Bold))
        titulo.setStyleSheet("color: #000000;")
        header_layout.addWidget(titulo)
        
        header_layout.addStretch()
        
        btn_agregar = QPushButton("Agregar Membresía")
        btn_agregar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        btn_agregar.clicked.connect(self.agregar_membresia)
        header_layout.addWidget(btn_agregar)
        
        layout.addLayout(header_layout)
        
        # Filtros
        filtros_layout = QHBoxLayout()
        label_filtro = QLabel("Filtro:")
        label_filtro.setStyleSheet("color: #000000;")
        filtros_layout.addWidget(label_filtro)
        
        self.btn_todos = QPushButton("Todos")
        self.btn_activas = QPushButton("Activas")
        self.btn_por_vencer = QPushButton("Por Vencer")
        self.btn_vencidas = QPushButton("Vencidas")
        
        # Estilos para los botones de filtro
        estilo_botones = """
            QPushButton {
                color: #000000;
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:checked {
                background-color: #3498db;
                color: white;
                border: 1px solid #2980b9;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:checked:hover {
                background-color: #2980b9;
            }
        """
        
        for btn, filtro in [(self.btn_todos, "Todos"), (self.btn_activas, ESTADO_ACTIVA),
                            (self.btn_por_vencer, ESTADO_POR_VENCER), (self.btn_vencidas, ESTADO_VENCIDA)]:
            btn.setCheckable(True)
            btn.setStyleSheet(estilo_botones)
            btn.clicked.connect(lambda checked, f=filtro: self.cambiar_filtro(f))
            filtros_layout.addWidget(btn)
        
        self.btn_todos.setChecked(True)
        filtros_layout.addStretch()
        
        layout.addLayout(filtros_layout)
        
        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(["Cliente", "Teléfono", "Inicio", "Vencimiento", "Monto", "Estado"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setAlternatingRowColors(False)
        self.tabla.setStyleSheet("""
            QTableWidget {
                gridline-color: #d3d3d3;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                font-weight: bold;
                border: none;
            }
        """)
        
        layout.addWidget(self.tabla)
        
        self.setLayout(layout)
    
    def cambiar_filtro(self, filtro):
        """Cambia el filtro aplicado"""
        self.filtro_actual = filtro
        
        # Actualizar botones
        self.btn_todos.setChecked(filtro == "Todos")
        self.btn_activas.setChecked(filtro == ESTADO_ACTIVA)
        self.btn_por_vencer.setChecked(filtro == ESTADO_POR_VENCER)
        self.btn_vencidas.setChecked(filtro == ESTADO_VENCIDA)
        
        self.cargar_datos()
    
    def cargar_datos(self):
        """Carga los datos de membresías"""
        if self.filtro_actual == "Todos":
            membresias = membresia_service.listar_membresias()
        else:
            membresias = membresia_service.listar_membresias(estado=self.filtro_actual)
        
        self.tabla.setRowCount(len(membresias))
        
        for i, membresia in enumerate(membresias):
            # Cliente - color negro
            cliente_item = QTableWidgetItem(membresia['cliente_nombre'])
            cliente_item.setForeground(QColor("#000000"))
            self.tabla.setItem(i, 0, cliente_item)
            
            # Teléfono
            self.tabla.setItem(i, 1, QTableWidgetItem(membresia.get('cliente_telefono', '')))
            
            # Inicio - color negro
            inicio_item = QTableWidgetItem(membresia['fecha_inicio'])
            inicio_item.setForeground(QColor("#000000"))
            self.tabla.setItem(i, 2, inicio_item)
            
            # Vencimiento - color negro
            vencimiento_item = QTableWidgetItem(membresia['fecha_vencimiento'])
            vencimiento_item.setForeground(QColor("#000000"))
            self.tabla.setItem(i, 3, vencimiento_item)
            
            # Monto - color verde
            monto_item = QTableWidgetItem(f"${membresia['monto']:,.0f}")
            monto_item.setForeground(QColor("#27ae60"))
            self.tabla.setItem(i, 4, monto_item)
            
            estado_item = QTableWidgetItem(membresia['estado'])
            
            # Colorear según estado
            if membresia['estado'] == ESTADO_ACTIVA:
                estado_item.setForeground(QColor("#27ae60"))
            elif membresia['estado'] == ESTADO_POR_VENCER:
                estado_item.setForeground(QColor("#f39c12"))
            elif membresia['estado'] == ESTADO_VENCIDA:
                estado_item.setForeground(QColor("#e74c3c"))
            
            self.tabla.setItem(i, 5, estado_item)
    
    def agregar_membresia(self):
        """Abre diálogo para agregar membresía"""
        dialog = AgregarMembresiaDialog(self)
        if dialog.exec():
            datos = dialog.obtener_datos()
            try:
                # Crear membresía
                membresia_id = membresia_service.crear_membresia(
                    cliente_id=datos['cliente_id'],
                    fecha_inicio=datos['fecha_inicio'],
                    monto=datos['monto']
                )
                
                # Obtener datos completos de la membresía
                membresia = membresia_service.obtener_membresia(membresia_id)
                cliente = cliente_service.obtener_cliente(datos['cliente_id'])
                
                # Generar factura
                ruta_factura = generar_factura_membresia(membresia, cliente)
                
                # Recargar datos
                self.cargar_datos()
                
                # Preguntar si desea ver la factura
                respuesta = QMessageBox.question(
                    self,
                    "Membresía Creada",
                    f"Membresía creada exitosamente.\nFactura #{membresia_id} generada.\n\n¿Desea abrir la factura?",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if respuesta == QMessageBox.Yes:
                    abrir_factura(ruta_factura)
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al crear membresía: {str(e)}")
