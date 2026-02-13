"""Vista de gestión de pagos"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QTableWidget, QTableWidgetItem, QHeaderView, QLabel,
                               QDialog, QFormLayout, QLineEdit, QDateEdit, QComboBox,
                               QMessageBox, QDialogButtonBox)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor
from datetime import date
from services import pago_service, cliente_service, membresia_service
from services import inventario_service
from utils.factura_generator import generar_factura_pago, abrir_factura
from pathlib import Path



class RegistrarPagoDialog(QDialog):
    """Diálogo para registrar o editar un pago"""
    def __init__(self, parent=None, pago=None):
        super().__init__(parent)
        self.pago = pago
        self.setWindowTitle("Editar Pago" if pago else "Registrar Pago")
        self.setMinimumWidth(400)
        self.init_ui()
        
        if pago:
            self.cargar_datos_pago()
    
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
            QComboBox QAbstractItemView {
                color: black;
                background-color: white;
                selection-background-color: #3498db;
                selection-color: black;
            }
            QCalendarWidget QAbstractItemView {
                selection-background-color: #3498db;
                selection-color: black;
                color: black;
            }
            QCalendarWidget QWidget {
                color: black;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #3498db;
            }
            QCalendarWidget QToolButton {
                color: white;
                background-color: #3498db;
            }
            QCalendarWidget QMenu {
                color: black;
                background-color: white;
            }
            QCalendarWidget QSpinBox {
                color: white;
                background-color: #3498db;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: black;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar QToolButton#qt_calendar_prevmonth,
            QCalendarWidget QWidget#qt_calendar_navigationbar QToolButton#qt_calendar_nextmonth {
                qproperty-icon: none;
            }
            QCalendarWidget QAbstractItemView::item:disabled {
                color: #cccccc;
            }
            QCalendarWidget QTableView::item:selected {
                background-color: #3498db;
                color: white;
            }
            QCalendarWidget QWidget {
                alternate-background-color: white;
            }
            QCalendarWidget QAbstractItemView:enabled[isHeaderRow="true"] {
                color: white;
                font-weight: bold;
                background-color: #3498db;
            }
            QCalendarWidget QTableView {
                color: black;
            }
            QPushButton {
                color: black;
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
        # Validador: solo números y un punto decimal
        from PySide6.QtGui import QRegularExpressionValidator
        from PySide6.QtCore import QRegularExpression
        validator_monto = QRegularExpressionValidator(QRegularExpression(r"^\d*\.?\d*$"))
        self.monto.setValidator(validator_monto)
        layout.addRow("Monto:", self.monto)
        
        # Método de pago
        self.metodo = QComboBox()
        self.metodo.addItems(["Efectivo", "Tarjeta", "Transferencia", "Otro"])
        layout.addRow("Método:", self.metodo)
        
        # Concepto (Tipo)
        self.concepto = QComboBox()
        self.concepto.addItems(["Pago de día", "Producto"])
        layout.addRow("Concepto:", self.concepto)

        # Selector de producto (oculto por defecto)
        self.combo_producto = QComboBox()
        self.combo_producto.setVisible(False)
        layout.addRow("Producto:", self.combo_producto)

        # Campo cantidad (oculto por defecto)
        self.input_cantidad = QLineEdit()
        self.input_cantidad.setPlaceholderText("Cantidad")
        self.input_cantidad.setVisible(False)
        layout.addRow("Cantidad:", self.input_cantidad)

        # Cargar productos
        self.cargar_productos()

        # Detectar cambio de concepto
        self.concepto.currentTextChanged.connect(self.toggle_producto_fields)

        
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

    def cargar_productos(self):
        """Carga productos en el combo"""
        productos = inventario_service.listar_productos()
        self.combo_producto.clear()

        for producto in productos:
            self.combo_producto.addItem(producto['nombre'], producto['id'])

    def toggle_producto_fields(self, texto):
        """Muestra u oculta campos según concepto"""
        es_producto = texto == "Producto"
        self.combo_producto.setVisible(es_producto)
        self.input_cantidad.setVisible(es_producto)
    
    def cargar_datos_pago(self):
        """Carga los datos del pago a editar"""
        if not self.pago:
            return
        
        # Seleccionar cliente
        for i in range(self.combo_cliente.count()):
            if self.combo_cliente.itemData(i) == self.pago['cliente_id']:
                self.combo_cliente.setCurrentIndex(i)
                break
        
        # Fecha
        fecha_parts = self.pago['fecha'].split('-')
        self.fecha.setDate(QDate(int(fecha_parts[0]), int(fecha_parts[1]), int(fecha_parts[2])))
        
        # Monto
        self.monto.setText(str(self.pago['monto']))
        
        # Método
        metodo = self.pago.get('metodo_pago', 'Efectivo')
        index = self.metodo.findText(metodo)
        if index >= 0:
            self.metodo.setCurrentIndex(index)
        
        # Concepto
        self.concepto.setText(self.pago.get('concepto', ''))
    
    def aceptar(self):
        """Valida y acepta el diálogo"""
        if self.combo_cliente.currentData() is None:
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setText("Seleccione un cliente")
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
            msg.exec()
            return
        
        try:
            monto = float(self.monto.text().replace(',', '.'))
            if monto <= 0:
                raise ValueError()
        except ValueError:
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setText("Ingrese un monto válido mayor a 0 (puede usar decimales, ej: 0.50)")
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
            msg.exec()
            return
        
        self.accept()
    
    def obtener_datos(self):
        """Retorna los datos ingresados"""
        fecha = self.fecha.date()
        cliente_id = self.combo_cliente.currentData()
        concepto_texto = self.concepto.currentText()

        datos = {
            'cliente_id': cliente_id,
            'fecha': date(fecha.year(), fecha.month(), fecha.day()),
            'monto': float(self.monto.text()),
            'metodo': self.metodo.currentText(),
            'concepto': concepto_texto
        }

        if concepto_texto == "Producto":
            producto_id = self.combo_producto.currentData()
            try:
                cantidad = int(self.input_cantidad.text())
                if cantidad <= 0:
                    raise ValueError()
            except:
                QMessageBox.warning(self, "Error", "Cantidad inválida")
                return {}

            datos['producto_id'] = producto_id
            datos['cantidad'] = cantidad

        return datos


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
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2980b9;
                color: white;
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
                color: black;
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
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels(["Cliente", "Fecha", "Monto", "Método", "Concepto", "Factura", "Acciones"])
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
            item_monto = QTableWidgetItem(f"${pago['monto']:,.2f}")
            item_monto.setForeground(QColor("#27ae60"))
            self.tabla.setItem(i, 2, item_monto)
            
            # Método - negro
            item_metodo = QTableWidgetItem(pago['metodo'])
            item_metodo.setForeground(Qt.black)
            self.tabla.setItem(i, 3, item_metodo)
            
            # Concepto - negro
            item_concepto = QTableWidgetItem(pago.get('concepto', ''))
            item_concepto.setForeground(Qt.black)
            self.tabla.setItem(i, 4, item_concepto)
            
            # Botón Ver Factura
            btn_ver_factura = QPushButton("Ver Factura")
            btn_ver_factura.setStyleSheet("""
                QPushButton {
                    background-color: #9b59b6;
                    color: white;
                    padding: 5px 15px;
                    border: none;
                    border-radius: 3px;
                    font-weight: bold;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #8e44ad;
                    color: white;
                }
            """)
            btn_ver_factura.clicked.connect(lambda checked, p=pago: self.ver_factura_pago(p))
            self.tabla.setCellWidget(i, 5, btn_ver_factura)
            
            # Botones de acciones
            acciones_widget = QWidget()
            acciones_layout = QHBoxLayout(acciones_widget)
            acciones_layout.setContentsMargins(5, 0, 5, 0)
            acciones_layout.setSpacing(5)
            
            btn_editar = QPushButton("Editar")
            btn_editar.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    padding: 5px 15px;
                    border: none;
                    border-radius: 3px;
                    font-weight: bold;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                    color: white;
                }
            """)
            btn_editar.clicked.connect(lambda checked, p=pago: self.editar_pago(p))
            acciones_layout.addWidget(btn_editar)
            
            btn_eliminar = QPushButton("Eliminar")
            btn_eliminar.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    padding: 5px 15px;
                    border: none;
                    border-radius: 3px;
                    font-weight: bold;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                    color: white;
                }
            """)
            btn_eliminar.clicked.connect(lambda checked, pid=pago['id']: self.eliminar_pago(pid))
            acciones_layout.addWidget(btn_eliminar)
            
            self.tabla.setCellWidget(i, 6, acciones_widget)
    
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
            item_monto = QTableWidgetItem(f"${pago['monto']:,.2f}")
            item_monto.setForeground(QColor("#27ae60"))
            self.tabla.setItem(i, 2, item_monto)
            
            # Método - negro
            item_metodo = QTableWidgetItem(pago['metodo'])
            item_metodo.setForeground(Qt.black)
            self.tabla.setItem(i, 3, item_metodo)
            
            # Concepto - negro
            item_concepto = QTableWidgetItem(pago.get('concepto', ''))
            item_concepto.setForeground(Qt.black)
            self.tabla.setItem(i, 4, item_concepto)
            
            # Botón Ver Factura
            btn_ver_factura = QPushButton("Ver Factura")
            btn_ver_factura.setStyleSheet("""
                QPushButton {
                    background-color: #9b59b6;
                    color: white;
                    padding: 5px 15px;
                    border: none;
                    border-radius: 3px;
                    font-weight: bold;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #8e44ad;
                    color: white;
                }
            """)
            btn_ver_factura.clicked.connect(lambda checked, p=pago: self.ver_factura_pago(p))
            self.tabla.setCellWidget(i, 5, btn_ver_factura)
            
            # Botones de acciones
            acciones_widget = QWidget()
            acciones_layout = QHBoxLayout(acciones_widget)
            acciones_layout.setContentsMargins(5, 0, 5, 0)
            acciones_layout.setSpacing(5)
            
            btn_editar = QPushButton("Editar")
            btn_editar.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    padding: 5px 15px;
                    border: none;
                    border-radius: 3px;
                    font-weight: bold;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                    color: white;
                }
            """)
            btn_editar.clicked.connect(lambda checked, p=pago: self.editar_pago(p))
            acciones_layout.addWidget(btn_editar)
            
            btn_eliminar = QPushButton("Eliminar")
            btn_eliminar.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    padding: 5px 15px;
                    border: none;
                    border-radius: 3px;
                    font-weight: bold;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                    color: white;
                }
            """)
            btn_eliminar.clicked.connect(lambda checked, pid=pago['id']: self.eliminar_pago(pid))
            acciones_layout.addWidget(btn_eliminar)
            
            self.tabla.setCellWidget(i, 6, acciones_widget)
    
    def actualizar_total_mes(self):
        """Actualiza el total de pagos del mes"""
        total = pago_service.calcular_total_mes()
        self.label_total.setText(f"Total del mes: ${total:,.2f}")
    
    def registrar_pago(self):
        """Abre diálogo para registrar pago"""
        dialog = RegistrarPagoDialog(self)
        if dialog.exec():
            datos = dialog.obtener_datos()
            
            if not datos:
                return
            
            ok, resultado = pago_service.crear_pago(
                cliente_id=datos['cliente_id'],
                fecha_pago=datos['fecha'],
                monto=datos['monto'],
                metodo=datos['metodo'],
                concepto=datos['concepto'],
                producto_id=datos.get('producto_id'),
                cantidad=datos.get('cantidad', 1)
            )

            if not ok:
                QMessageBox.warning(self, "Error", resultado)
                return

            pago_id = resultado

            
            # Generar factura
            pago = pago_service.obtener_pago(pago_id)
            cliente = cliente_service.obtener_cliente(datos['cliente_id'])
            ruta_factura = generar_factura_pago(pago, cliente)
            
            self.cargar_datos()
            self.actualizar_total_mes()
            
            # Mensaje con estilo y botón para ver factura
            msg = QMessageBox(self)
            msg.setWindowTitle("Éxito")
            msg.setText("Pago registrado correctamente")
            msg.setInformativeText("¿Desea ver la factura generada?")
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
            btn_ver = msg.addButton("Ver Factura", QMessageBox.ActionRole)
            msg.addButton("Cerrar", QMessageBox.RejectRole)
            msg.exec()
            
            if msg.clickedButton() == btn_ver:
                abrir_factura(ruta_factura)
    
    def editar_pago(self, pago):
        """Abre diálogo para editar un pago"""
        dialog = RegistrarPagoDialog(self, pago=pago)
        if dialog.exec():
            datos = dialog.obtener_datos()
            pago_service.actualizar_pago(
                pago_id=pago['id'],
                cliente_id=datos['cliente_id'],
                fecha_pago=datos['fecha'],
                monto=datos['monto'],
                metodo=datos['metodo'],
                concepto=datos['concepto']
            )
            self.cargar_datos()
            self.actualizar_total_mes()
            # Mensaje con estilo
            msg = QMessageBox(self)
            msg.setWindowTitle("Éxito")
            msg.setText("Pago actualizado correctamente")
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
    
    def ver_factura_pago(self, pago):
        """Abre la factura de un pago"""
        try:
            # Obtener información completa del cliente
            cliente = cliente_service.obtener_cliente(pago['cliente_id'])
            
            # Generar o buscar la factura
            ruta_factura = Path.home() / "KyoGym" / "Facturas" / f"Factura_Pago_{pago['id']}.pdf"
            
            # Si la factura no existe, generarla
            if not ruta_factura.exists():
                ruta_factura = generar_factura_pago(pago, cliente)
            
            # Abrir la factura
            abrir_factura(str(ruta_factura))
            
        except Exception as e:
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setText(f"No se pudo abrir la factura: {str(e)}")
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
                    background-color: #e74c3c;
                    color: white;
                    padding: 8px 20px;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 13px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            msg.exec()
    
    def eliminar_pago(self, pago_id):
        """Elimina un pago"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Confirmar eliminación")
        msg.setText("¿Está seguro de eliminar este pago?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
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
        respuesta = msg.exec()
        
        if respuesta == QMessageBox.Yes:
            try:
                pago_service.eliminar_pago(pago_id)
                self.cargar_datos()
                self.actualizar_total_mes()
                # Mensaje con estilo
                msg = QMessageBox(self)
                msg.setWindowTitle("Éxito")
                msg.setText("Pago eliminado correctamente")
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
            except Exception as e:
                msg = QMessageBox(self)
                msg.setWindowTitle("Error")
                msg.setText(f"Error al eliminar pago: {str(e)}")
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
                        background-color: #e74c3c;
                        color: white;
                        padding: 8px 20px;
                        border: none;
                        border-radius: 4px;
                        font-weight: bold;
                        font-size: 13px;
                        min-width: 80px;
                    }
                    QPushButton:hover {
                        background-color: #c0392b;
                    }
                """)
                msg.exec()
