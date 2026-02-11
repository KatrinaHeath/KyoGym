"""Vista de gestión de membresías"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QTableWidget, QTableWidgetItem, QHeaderView, QLabel,
                               QDialog, QFormLayout, QLineEdit, QDateEdit, QComboBox,
                               QMessageBox, QDialogButtonBox)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor
from datetime import date
from pathlib import Path
from services import membresia_service, cliente_service
from utils.constants import ESTADO_ACTIVA, ESTADO_POR_VENCER, ESTADO_VENCIDA
from utils.factura_generator import generar_factura_membresia, abrir_factura


class AgregarMembresiaDialog(QDialog):
    """Diálogo para agregar o editar membresía"""
    def __init__(self, parent=None, membresia=None):
        super().__init__(parent)
        self.membresia = membresia
        self.setWindowTitle("Editar Membresía" if membresia else "Nueva Membresía")
        self.setMinimumWidth(400)
        self.init_ui()
        
        if membresia:
            self.cargar_datos_membresia()
    
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
        
        # Fecha de inicio
        self.fecha_inicio = QDateEdit()
        self.fecha_inicio.setDate(QDate.currentDate())
        self.fecha_inicio.setCalendarPopup(True)
        layout.addRow("Fecha Inicio:", self.fecha_inicio)
        
        # Monto
        self.monto = QLineEdit()
        self.monto.setPlaceholderText("0.00")
        # Validador: solo números y un punto decimal
        from PySide6.QtGui import QRegularExpressionValidator
        from PySide6.QtCore import QRegularExpression
        validator_monto = QRegularExpressionValidator(QRegularExpression(r"^\d*\.?\d*$"))
        self.monto.setValidator(validator_monto)
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
    
    def cargar_datos_membresia(self):
        """Carga los datos de la membresía a editar"""
        if not self.membresia:
            return
        
        # Seleccionar cliente
        for i in range(self.combo_cliente.count()):
            if self.combo_cliente.itemData(i) == self.membresia['cliente_id']:
                self.combo_cliente.setCurrentIndex(i)
                break
        
        # Fecha inicio
        fecha_parts = self.membresia['fecha_inicio'].split('-')
        self.fecha_inicio.setDate(QDate(int(fecha_parts[0]), int(fecha_parts[1]), int(fecha_parts[2])))
        
        # Monto
        self.monto.setText(str(self.membresia['monto']))
    
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
            float(self.monto.text())
        except ValueError:
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setText("Ingrese un monto válido")
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
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #229954;
                color: white;
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
                color: black;
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
        self.tabla.setColumnCount(8)
        self.tabla.setHorizontalHeaderLabels(["Cliente", "Teléfono", "Inicio", "Vencimiento", "Monto", "Estado", "Factura", "Acciones"])
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
            
            # Teléfono - color negro
            telefono_item = QTableWidgetItem(membresia.get('cliente_telefono', ''))
            telefono_item.setForeground(QColor("#000000"))
            self.tabla.setItem(i, 1, telefono_item)
            
            # Inicio - color negro
            inicio_item = QTableWidgetItem(membresia['fecha_inicio'])
            inicio_item.setForeground(QColor("#000000"))
            self.tabla.setItem(i, 2, inicio_item)
            
            # Vencimiento - color negro
            vencimiento_item = QTableWidgetItem(membresia['fecha_vencimiento'])
            vencimiento_item.setForeground(QColor("#000000"))
            self.tabla.setItem(i, 3, vencimiento_item)
            
            # Monto - color verde
            monto_item = QTableWidgetItem(f"${membresia['monto']:,.2f}")
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
            btn_ver_factura.clicked.connect(lambda checked, m=membresia: self.ver_factura_membresia(m))
            self.tabla.setCellWidget(i, 6, btn_ver_factura)
            
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
            btn_editar.clicked.connect(lambda checked, m=membresia: self.editar_membresia(m))
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
            btn_eliminar.clicked.connect(lambda checked, mid=membresia['id']: self.eliminar_membresia(mid))
            acciones_layout.addWidget(btn_eliminar)
            
            self.tabla.setCellWidget(i, 7, acciones_widget)
    
    def agregar_membresia(self):
        """Abre diálogo para agregar membresía"""
        dialog = AgregarMembresiaDialog(self)
        if dialog.exec():
            datos = dialog.obtener_datos()
            try:
                # Verificar si el cliente ya tiene una membresía activa
                membresia_activa = membresia_service.obtener_membresia_activa(datos['cliente_id'])
                if membresia_activa:
                    cliente = cliente_service.obtener_cliente(datos['cliente_id'])
                    msg = QMessageBox(self)
                    msg.setWindowTitle("Membresía Activa")
                    msg.setText(f"El cliente {cliente['nombre']} ya tiene una membresía activa.")
                    msg.setInformativeText(f"Estado: {membresia_activa['estado']}\nVencimiento: {membresia_activa['fecha_vencimiento']}")
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
                    return
                
                # Importar pago_service aquí para evitar imports circulares
                from services import pago_service
                
                # Crear el pago primero
                pago_id = pago_service.crear_pago(
                    cliente_id=datos['cliente_id'],
                    monto=datos['monto'],
                    metodo="Efectivo",  # Método por defecto
                    fecha_pago=datos['fecha_inicio'],
                    concepto="Pago de membresía"
                )
                
                # Crear membresía con el pago_id
                membresia_id = membresia_service.crear_membresia(
                    cliente_id=datos['cliente_id'],
                    fecha_inicio=datos['fecha_inicio'],
                    monto=datos['monto'],
                    pago_id=pago_id
                )
                
                # Obtener datos completos de la membresía
                membresia = membresia_service.obtener_membresia(membresia_id)
                cliente = cliente_service.obtener_cliente(datos['cliente_id'])
                
                # Generar factura
                ruta_factura = generar_factura_membresia(membresia, cliente)
                
                # Recargar datos
                self.cargar_datos()
                
                # Preguntar si desea ver la factura
                respuesta_msg = QMessageBox(self)
                respuesta_msg.setWindowTitle("Membresía Creada")
                respuesta_msg.setText(f"Membresía creada exitosamente.\nFactura #{membresia_id} generada.\n\n¿Desea abrir la factura?")
                respuesta_msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                respuesta_msg.setDefaultButton(QMessageBox.Yes)
                respuesta_msg.setStyleSheet("""
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
                respuesta = respuesta_msg.exec()
                
                if respuesta == QMessageBox.Yes:
                    abrir_factura(ruta_factura)
                    
            except Exception as e:
                msg = QMessageBox(self)
                msg.setWindowTitle("Error")
                msg.setText(f"Error al crear membresía: {str(e)}")
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
    
    def editar_membresia(self, membresia):
        """Abre diálogo para editar una membresía"""
        dialog = AgregarMembresiaDialog(self, membresia=membresia)
        if dialog.exec():
            datos = dialog.obtener_datos()
            try:
                membresia_service.actualizar_membresia(
                    membresia_id=membresia['id'],
                    cliente_id=datos['cliente_id'],
                    tipo="Mensual",
                    fecha_inicio=datos['fecha_inicio'],
                    monto=datos['monto']
                )
                self.cargar_datos()
                
                # Mensaje con estilo
                msg = QMessageBox(self)
                msg.setWindowTitle("Éxito")
                msg.setText("Membresía actualizada exitosamente")
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
                msg.setText(f"Error al actualizar membresía: {str(e)}")
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
    
    def ver_factura_membresia(self, membresia):
        """Abre la factura de una membresía"""
        try:
            # Obtener información completa del cliente
            cliente = cliente_service.obtener_cliente(membresia['cliente_id'])
            
            # Generar o buscar la factura
            ruta_factura = Path.home() / "KyoGym" / "Facturas" / f"Factura_{membresia['id']}.pdf"
            
            # Si la factura no existe, generarla
            if not ruta_factura.exists():
                ruta_factura = generar_factura_membresia(membresia, cliente)
            
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
    
    def eliminar_membresia(self, membresia_id):
        """Elimina una membresía"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Confirmar eliminación")
        msg.setText("¿Está seguro de eliminar esta membresía?")
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
                membresia_service.eliminar_membresia(membresia_id)
                self.cargar_datos()
                # Mensaje con estilo
                msg = QMessageBox(self)
                msg.setWindowTitle("Éxito")
                msg.setText("Membresía eliminada correctamente")
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
                msg.setText(f"Error al eliminar membresía: {str(e)}")
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

