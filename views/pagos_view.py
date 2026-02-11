"""Vista de gestión de pagos"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QTableWidget, QTableWidgetItem, QHeaderView, QLabel,
                               QDialog, QFormLayout, QLineEdit, QDateEdit, QComboBox,
                               QMessageBox, QDialogButtonBox)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor, QBrush
from datetime import date
from services import pago_service, cliente_service, membresia_service


class RegistrarPagoDialog(QDialog):
    """Diálogo para registrar un nuevo pago"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar Pago")
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
        
        # Fecha
        self.fecha = QDateEdit()
        self.fecha.setDate(QDate.currentDate())
        self.fecha.setCalendarPopup(True)
        layout.addRow("Fecha:", self.fecha)
        
        # Monto
        self.monto = QLineEdit()
        self.monto.setPlaceholderText("0.00")
        layout.addRow("Monto:", self.monto)
        
        # Método de pago
        self.metodo = QComboBox()
        self.metodo.addItems(["Efectivo", "Tarjeta", "Transferencia", "Otro"])
        layout.addRow("Método:", self.metodo)
        
        # Concepto
        self.concepto = QLineEdit()
        self.concepto.setPlaceholderText("Membresía mensual, renovación, etc.")
        layout.addRow("Concepto:", self.concepto)
        
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
            monto = float(self.monto.text())
            if monto <= 0:
                raise ValueError()
        except ValueError:
            QMessageBox.warning(self, "Error", "Ingrese un monto válido mayor a 0")
            return
        
        self.accept()
    
    def obtener_datos(self):
        """Retorna los datos ingresados"""
        fecha = self.fecha.date()
        
        # Obtener membresía activa del cliente
        cliente_id = self.combo_cliente.currentData()
        membresia = membresia_service.obtener_membresia_activa(cliente_id)
        membresia_id = membresia['id'] if membresia else None
        
        return {
            'cliente_id': cliente_id,
            'fecha': date(fecha.year(), fecha.month(), fecha.day()),
            'monto': float(self.monto.text()),
            'metodo': self.metodo.currentText(),
            'concepto': self.concepto.text(),
            'membresia_id': membresia_id
        }


class PagosView(QWidget):
    """Vista de gestión de pagos"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.cargar_datos()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Encabezado
        header_layout = QHBoxLayout()
        
        titulo = QLabel("Pagos")
        titulo.setFont(QFont("Arial", 24, QFont.Bold))
        titulo.setStyleSheet("color: #000000;")
        header_layout.addWidget(titulo)
        
        header_layout.addStretch()
        
        btn_registrar = QPushButton("Registrar Pago")
        btn_registrar.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        btn_registrar.clicked.connect(self.registrar_pago)
        header_layout.addWidget(btn_registrar)
        
        layout.addLayout(header_layout)
        
        # Filtros rápidos
        filtros_layout = QHBoxLayout()
        label_filtro = QLabel("Ver:")
        label_filtro.setStyleSheet("color: #000000;")
        filtros_layout.addWidget(label_filtro)
        
        # Estilos para botones de filtro
        estilo_botones = """
            QPushButton {
                background-color: #f0f0f0;
                color: #000000;
                padding: 8px 16px;
                border: 2px solid #d0d0d0;
                border-radius: 5px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border: 2px solid #b0b0b0;
            }
            QPushButton:checked {
                background-color: #2196F3;
                color: white;
                border: 2px solid #1976D2;
            }
        """
        
        btn_todos = QPushButton("Todos")
        btn_mes = QPushButton("Este Mes")
        btn_ultimos = QPushButton("Últimos 50")
        
        btn_todos.clicked.connect(lambda: self.cargar_datos(limite=500))
        btn_mes.clicked.connect(self.cargar_pagos_mes)
        btn_ultimos.clicked.connect(lambda: self.cargar_datos(limite=50))
        
        for btn in [btn_todos, btn_mes, btn_ultimos]:
            btn.setStyleSheet(estilo_botones)
            filtros_layout.addWidget(btn)
        
        filtros_layout.addStretch()
        
        # Total del mes
        self.label_total = QLabel("Total del mes: $0")
        self.label_total.setFont(QFont("Arial", 14, QFont.Bold))
        self.label_total.setStyleSheet("color: #27ae60;")
        filtros_layout.addWidget(self.label_total)
        
        layout.addLayout(filtros_layout)
        
        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["Cliente", "Fecha", "Monto", "Método", "Concepto"])
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
        self.actualizar_total_mes()
    
    def cargar_datos(self, limite=100):
        """Carga los datos de pagos"""
        pagos = pago_service.listar_pagos(limite=limite)
        
        self.tabla.setRowCount(len(pagos))
        
        for i, pago in enumerate(pagos):
            # Cliente - negro
            item_cliente = QTableWidgetItem(pago['cliente_nombre'])
            item_cliente.setForeground(Qt.black)
            self.tabla.setItem(i, 0, item_cliente)
            
            # Fecha - negro
            item_fecha = QTableWidgetItem(pago['fecha'])
            item_fecha.setForeground(Qt.black)
            self.tabla.setItem(i, 1, item_fecha)
            
            # Monto - verde
            item_monto = QTableWidgetItem(f"${pago['monto']:,.0f}")
            item_monto.setForeground(QBrush(QColor('#27ae60')))
            self.tabla.setItem(i, 2, item_monto)
            
            # Método - negro
            item_metodo = QTableWidgetItem(pago['metodo'])
            item_metodo.setForeground(Qt.black)
            self.tabla.setItem(i, 3, item_metodo)
            
            # Concepto - negro
            item_concepto = QTableWidgetItem(pago.get('concepto', ''))
            item_concepto.setForeground(Qt.black)
            self.tabla.setItem(i, 4, item_concepto)
    
    def cargar_pagos_mes(self):
        """Carga solo los pagos del mes actual"""
        pagos = pago_service.obtener_pagos_del_mes()
        
        self.tabla.setRowCount(len(pagos))
        
        for i, pago in enumerate(pagos):
            # Cliente - negro
            item_cliente = QTableWidgetItem(pago['cliente_nombre'])
            item_cliente.setForeground(Qt.black)
            self.tabla.setItem(i, 0, item_cliente)
            
            # Fecha - negro
            item_fecha = QTableWidgetItem(pago['fecha'])
            item_fecha.setForeground(Qt.black)
            self.tabla.setItem(i, 1, item_fecha)
            
            # Monto - verde
            item_monto = QTableWidgetItem(f"${pago['monto']:,.0f}")
            item_monto.setForeground(QBrush(QColor('#27ae60')))
            self.tabla.setItem(i, 2, item_monto)
            
            # Método - negro
            item_metodo = QTableWidgetItem(pago['metodo'])
            item_metodo.setForeground(Qt.black)
            self.tabla.setItem(i, 3, item_metodo)
            
            # Concepto - negro
            item_concepto = QTableWidgetItem(pago.get('concepto', ''))
            item_concepto.setForeground(Qt.black)
            self.tabla.setItem(i, 4, item_concepto)
    
    def actualizar_total_mes(self):
        """Actualiza el total de pagos del mes"""
        total = pago_service.calcular_total_mes()
        self.label_total.setText(f"Total del mes: ${total:,.0f}")
    
    def registrar_pago(self):
        """Abre diálogo para registrar pago"""
        dialog = RegistrarPagoDialog(self)
        if dialog.exec():
            datos = dialog.obtener_datos()
            pago_service.crear_pago(
                cliente_id=datos['cliente_id'],
                fecha_pago=datos['fecha'],
                monto=datos['monto'],
                metodo=datos['metodo'],
                concepto=datos['concepto'],
                membresia_id=datos['membresia_id']
            )
            self.cargar_datos()
            self.actualizar_total_mes()
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Éxito")
            msg.setText("Pago registrado correctamente")
            msg.setStyleSheet("QLabel{ color: #2c3e50; } QPushButton{ padding:6px 12px; }")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
