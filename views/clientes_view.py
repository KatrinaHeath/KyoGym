"""Vista de gestión de clientes"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QTableWidget, QTableWidgetItem, QHeaderView, QLabel,
                               QDialog, QFormLayout, QLineEdit, QDateEdit, QComboBox,
                               QMessageBox, QDialogButtonBox, QFrame)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor
from datetime import date
from services import cliente_service


class AgregarClienteDialog(QDialog):
    """Diálogo para agregar/editar cliente"""
    def __init__(self, parent=None, cliente=None):
        super().__init__(parent)
        self.cliente = cliente
        self.setWindowTitle("Editar Cliente" if cliente else "Nuevo Cliente")
        self.setMinimumWidth(400)
        self.init_ui()
        
        if cliente:
            self.cargar_datos_cliente()
    
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
        
        # Nombre
        self.nombre = QLineEdit()
        self.nombre.setPlaceholderText("Ingrese el nombre completo")
        layout.addRow("Nombre:", self.nombre)
        
        # Teléfono
        self.telefono = QLineEdit()
        self.telefono.setPlaceholderText("+50767686213")
        layout.addRow("Teléfono:", self.telefono)
        
        # Sexo
        self.sexo = QComboBox()
        self.sexo.addItems(["Masculino", "Femenino", "Otro"])
        layout.addRow("Sexo:", self.sexo)
        
        # Fecha de nacimiento
        self.fecha_nacimiento = QDateEdit()
        self.fecha_nacimiento.setDate(QDate.currentDate().addYears(-25))
        self.fecha_nacimiento.setCalendarPopup(True)
        self.fecha_nacimiento.setDisplayFormat("dd/MM/yyyy")
        layout.addRow("Fecha de Nacimiento:", self.fecha_nacimiento)
        
        # Botones
        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botones.accepted.connect(self.aceptar)
        botones.rejected.connect(self.reject)
        layout.addRow(botones)
        
        self.setLayout(layout)
    
    def cargar_datos_cliente(self):
        """Carga los datos del cliente para editar"""
        self.nombre.setText(self.cliente['nombre'])
        self.telefono.setText(self.cliente['telefono'] or "")
        
        if self.cliente.get('sexo'):
            index = self.sexo.findText(self.cliente['sexo'])
            if index >= 0:
                self.sexo.setCurrentIndex(index)
        
        if self.cliente.get('fecha_nacimiento'):
            fecha = date.fromisoformat(self.cliente['fecha_nacimiento'])
            self.fecha_nacimiento.setDate(QDate(fecha.year, fecha.month, fecha.day))
    
    def aceptar(self):
        """Valida y acepta el diálogo"""
        if not self.nombre.text().strip():
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setText("El nombre es requerido")
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
        fecha = self.fecha_nacimiento.date()
        return {
            'nombre': self.nombre.text().strip(),
            'telefono': self.telefono.text().strip(),
            'sexo': self.sexo.currentText(),
            'fecha_nacimiento': date(fecha.year(), fecha.month(), fecha.day()).isoformat()
        }


class ClientesView(QWidget):
    """Vista de gestión de clientes"""
    def __init__(self):
        super().__init__()
        self.filtro_genero = None
        self.filtro_edad = None
        self.edad_minima = None
        self.edad_maxima = None
        self.init_ui()
        self.cargar_datos()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Encabezado
        header_layout = QHBoxLayout()
        
        titulo = QLabel("Clientes")
        titulo.setFont(QFont("Arial", 24, QFont.Bold))
        titulo.setStyleSheet("color: #000000;")
        header_layout.addWidget(titulo)
        
        header_layout.addStretch()
        
        # Búsqueda
        self.buscar_input = QLineEdit()
        self.buscar_input.setPlaceholderText("Buscar cliente...")
        self.buscar_input.setMinimumWidth(250)
        self.buscar_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                font-size: 13px;
                color: black;
            }
        """)
        self.buscar_input.textChanged.connect(self.cargar_datos)
        header_layout.addWidget(self.buscar_input)
        
        btn_agregar = QPushButton("Agregar Cliente")
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
        btn_agregar.clicked.connect(self.agregar_cliente)
        header_layout.addWidget(btn_agregar)
        
        layout.addLayout(header_layout)
        
        # Filtros
        filtros_layout = QHBoxLayout()
        
        # Filtros por género
        label_genero = QLabel("Género:")
        label_genero.setStyleSheet("color: #000000; font-weight: bold;")
        filtros_layout.addWidget(label_genero)
        
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
        
        self.btn_todos_genero = QPushButton("Todos")
        self.btn_masculino = QPushButton("Masculino")
        self.btn_femenino = QPushButton("Femenino")
        self.btn_otro = QPushButton("Otro")
        
        self.btn_todos_genero.setCheckable(True)
        self.btn_masculino.setCheckable(True)
        self.btn_femenino.setCheckable(True)
        self.btn_otro.setCheckable(True)
        self.btn_todos_genero.setChecked(True)
        
        self.btn_todos_genero.clicked.connect(lambda: self.cambiar_filtro_genero(None, self.btn_todos_genero))
        self.btn_masculino.clicked.connect(lambda: self.cambiar_filtro_genero("Masculino", self.btn_masculino))
        self.btn_femenino.clicked.connect(lambda: self.cambiar_filtro_genero("Femenino", self.btn_femenino))
        self.btn_otro.clicked.connect(lambda: self.cambiar_filtro_genero("Otro", self.btn_otro))
        
        for btn in [self.btn_todos_genero, self.btn_masculino, self.btn_femenino, self.btn_otro]:
            btn.setStyleSheet(estilo_botones)
            filtros_layout.addWidget(btn)
        
        # Separador
        separador = QLabel("|")
        separador.setStyleSheet("color: #d0d0d0; font-size: 18px; padding: 0 10px;")
        filtros_layout.addWidget(separador)
        
        # Filtros por edad
        label_edad = QLabel("Edad:")
        label_edad.setStyleSheet("color: #000000; font-weight: bold;")
        filtros_layout.addWidget(label_edad)
        
        self.btn_todas_edades = QPushButton("Todas")
        self.btn_todas_edades.setCheckable(True)
        self.btn_todas_edades.setChecked(True)
        self.btn_todas_edades.clicked.connect(lambda: self.cambiar_filtro_edad(None, self.btn_todas_edades))
        self.btn_todas_edades.setStyleSheet(estilo_botones)
        filtros_layout.addWidget(self.btn_todas_edades)
        
        # Filtro menor que
        label_menor = QLabel("Menor que:")
        label_menor.setStyleSheet("color: #000000;")
        filtros_layout.addWidget(label_menor)
        
        self.input_menor_que = QLineEdit()
        self.input_menor_que.setPlaceholderText("Edad")
        self.input_menor_que.setMaximumWidth(60)
        self.input_menor_que.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                font-size: 13px;
                color: black;
            }
        """)
        self.input_menor_que.textChanged.connect(self.aplicar_filtro_menor_que)
        filtros_layout.addWidget(self.input_menor_que)
        
        # Filtro mayor que
        label_mayor = QLabel("Mayor que:")
        label_mayor.setStyleSheet("color: #000000;")
        filtros_layout.addWidget(label_mayor)
        
        self.input_mayor_que = QLineEdit()
        self.input_mayor_que.setPlaceholderText("Edad")
        self.input_mayor_que.setMaximumWidth(60)
        self.input_mayor_que.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                font-size: 13px;
                color: black;
            }
        """)
        self.input_mayor_que.textChanged.connect(self.aplicar_filtro_mayor_que)
        filtros_layout.addWidget(self.input_mayor_que)
        
        filtros_layout.addStretch()
        
        layout.addLayout(filtros_layout)
        
        # Tabla de clientes
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(["Nombre", "Teléfono", "Edad", "Sexo", "Fecha Nacimiento", "Acciones"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setAlternatingRowColors(False)
        self.tabla.verticalHeader().setVisible(False)
        
        # Estilo igual a membresías
        self.tabla.setStyleSheet("""
            QTableWidget {
                gridline-color: #d3d3d3;
                font-size: 13px;
                background-color: white;
                border: 1px solid #e0e0e0;
            }
            QTableWidget::item {
                padding: 5px;
                color: #2c3e50;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: black;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                font-weight: bold;
                border: none;
            }
        """)
        
        # Ajustar columnas para que ocupen todo el espacio
        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.tabla)
        
        self.setLayout(layout)
    
    def cargar_datos(self):
        """Carga los clientes en la tabla"""
        buscar = self.buscar_input.text() if hasattr(self, 'buscar_input') else ""
        clientes = cliente_service.listar_clientes(buscar=buscar)
        
        self.tabla.setRowCount(len(clientes))
        
        for i, cliente in enumerate(clientes):
            # Nombre
            self.tabla.setItem(i, 0, QTableWidgetItem(cliente['nombre']))
            
            # Teléfono
            self.tabla.setItem(i, 1, QTableWidgetItem(cliente['telefono'] or "-"))
            
            # Edad
            fecha_nac = cliente.get('fecha_nacimiento', '')
            if fecha_nac:
                fecha = date.fromisoformat(fecha_nac)
                hoy = date.today()
                edad = hoy.year - fecha.year - ((hoy.month, hoy.day) < (fecha.month, fecha.day))
                self.tabla.setItem(i, 2, QTableWidgetItem(str(edad)))
            else:
                self.tabla.setItem(i, 2, QTableWidgetItem("-"))
            
            # Sexo
            self.tabla.setItem(i, 3, QTableWidgetItem(cliente.get('sexo', "-")))
            
            # Fecha de nacimiento
            if fecha_nac:
                fecha_texto = fecha.strftime("%d/%m/%Y")
            else:
                fecha_texto = "-"
            self.tabla.setItem(i, 4, QTableWidgetItem(fecha_texto))
            
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
            btn_editar.clicked.connect(lambda checked, c=cliente: self.editar_cliente(c))
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
            btn_eliminar.clicked.connect(lambda checked, cid=cliente['id']: self.eliminar_cliente(cid))
            acciones_layout.addWidget(btn_eliminar)
            
            self.tabla.setCellWidget(i, 5, acciones_widget)
    
    def agregar_cliente(self):
        """Muestra diálogo para agregar cliente"""
        dialog = AgregarClienteDialog(self)
        if dialog.exec() == QDialog.Accepted:
            datos = dialog.obtener_datos()
            try:
                # Verificar si el teléfono ya está registrado
                if datos['telefono']:
                    cliente_existente = cliente_service.verificar_telefono_existente(datos['telefono'])
                    if cliente_existente:
                        msg = QMessageBox(self)
                        msg.setWindowTitle("Teléfono en uso")
                        msg.setText(f"El número {datos['telefono']} ya está vinculado al cliente: {cliente_existente['nombre']}")
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
                
                cliente_service.crear_cliente(
                    nombre=datos['nombre'],
                    telefono=datos['telefono'],
                    sexo=datos['sexo'],
                    fecha_nacimiento=datos['fecha_nacimiento']
                )
                # Mensaje con estilo
                msg = QMessageBox(self)
                msg.setWindowTitle("Éxito")
                msg.setText("Cliente agregado exitosamente")
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
                self.cargar_datos()
            except Exception as e:
                msg = QMessageBox(self)
                msg.setWindowTitle("Error")
                msg.setText(f"Error al agregar cliente: {str(e)}")
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
    
    def editar_cliente(self, cliente):
        """Muestra diálogo para editar cliente"""
        dialog = AgregarClienteDialog(self, cliente)
        if dialog.exec() == QDialog.Accepted:
            datos = dialog.obtener_datos()
            try:
                # Verificar si el teléfono ya está registrado para otro cliente
                if datos['telefono']:
                    cliente_existente = cliente_service.verificar_telefono_existente(datos['telefono'], excluir_id=cliente['id'])
                    if cliente_existente:
                        msg = QMessageBox(self)
                        msg.setWindowTitle("Teléfono en uso")
                        msg.setText(f"El número {datos['telefono']} ya está vinculado al cliente: {cliente_existente['nombre']}")
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
                
                cliente_service.actualizar_cliente(
                    cliente_id=cliente['id'],
                    nombre=datos['nombre'],
                    telefono=datos['telefono'],
                    sexo=datos['sexo'],
                    fecha_nacimiento=datos['fecha_nacimiento']
                )
                # Mensaje con estilo
                msg = QMessageBox(self)
                msg.setWindowTitle("Éxito")
                msg.setText("Cliente actualizado exitosamente")
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
                self.cargar_datos()
            except Exception as e:
                msg = QMessageBox(self)
                msg.setWindowTitle("Error")
                msg.setText(f"Error al actualizar cliente: {str(e)}")
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
    
    def eliminar_cliente(self, cliente_id):
        """Elimina un cliente"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Confirmar eliminación")
        msg.setText("¿Está seguro de eliminar este cliente?")
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
                cliente_service.eliminar_cliente(cliente_id)
                # Mensaje con estilo
                msg = QMessageBox(self)
                msg.setWindowTitle("Éxito")
                msg.setText("Cliente eliminado exitosamente")
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
                self.cargar_datos()
            except Exception as e:
                msg = QMessageBox(self)
                msg.setWindowTitle("Error")
                msg.setText(f"Error al eliminar cliente: {str(e)}")
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
    
    def cambiar_filtro_genero(self, genero, boton_activo):
        """Cambia el filtro de género"""
        # Desmarcar todos los botones de género
        for btn in [self.btn_todos_genero, self.btn_masculino, self.btn_femenino, self.btn_otro]:
            btn.setChecked(False)
        
        # Marcar el botón activo
        boton_activo.setChecked(True)
        
        # Actualizar filtro
        self.filtro_genero = genero
        self.aplicar_filtros()
    
    def cambiar_filtro_edad(self, rango_edad, boton_activo):
        """Cambia el filtro de edad"""
        # Desmarcar el botón "Todas"
        self.btn_todas_edades.setChecked(False)
        
        # Marcar el botón activo
        boton_activo.setChecked(True)
        
        # Limpiar los campos de entrada personalizados
        self.input_menor_que.clear()
        self.input_mayor_que.clear()
        self.edad_minima = None
        self.edad_maxima = None
        
        # Actualizar filtro
        self.filtro_edad = rango_edad
        self.aplicar_filtros()
    
    def aplicar_filtro_menor_que(self):
        """Aplica el filtro de edad menor que el valor ingresado"""
        # Desmarcar el botón "Todas"
        self.btn_todas_edades.setChecked(False)
        
        texto = self.input_menor_que.text().strip()
        
        if texto and texto.isdigit():
            self.edad_maxima = int(texto)
        else:
            self.edad_maxima = None
        
        # Si ambos campos están vacíos, marcar "Todas"
        if not self.input_menor_que.text().strip() and not self.input_mayor_que.text().strip():
            self.btn_todas_edades.setChecked(True)
        
        self.filtro_edad = "personalizado"
        self.aplicar_filtros()
    
    def aplicar_filtro_mayor_que(self):
        """Aplica el filtro de edad mayor que el valor ingresado"""
        # Desmarcar el botón "Todas"
        self.btn_todas_edades.setChecked(False)
        
        texto = self.input_mayor_que.text().strip()
        
        if texto and texto.isdigit():
            self.edad_minima = int(texto)
        else:
            self.edad_minima = None
        
        # Si ambos campos están vacíos, marcar "Todas"
        if not self.input_menor_que.text().strip() and not self.input_mayor_que.text().strip():
            self.btn_todas_edades.setChecked(True)
        
        self.filtro_edad = "personalizado"
        self.aplicar_filtros()
    
    def aplicar_filtros(self):
        """Aplica los filtros de género y edad a la tabla"""
        buscar = self.buscar_input.text() if hasattr(self, 'buscar_input') else ""
        clientes = cliente_service.listar_clientes(buscar=buscar)
        
        # Filtrar por género
        if self.filtro_genero:
            clientes = [c for c in clientes if c.get('sexo') == self.filtro_genero]
        
        # Filtrar por edad
        if self.filtro_edad == "personalizado" and (self.edad_minima is not None or self.edad_maxima is not None):
            hoy = date.today()
            clientes_filtrados = []
            
            for cliente in clientes:
                if cliente.get('fecha_nacimiento'):
                    fecha_nac = date.fromisoformat(cliente['fecha_nacimiento'])
                    edad = (hoy - fecha_nac).days // 365
                    
                    # Aplicar ambos filtros si están definidos
                    cumple_minimo = True if self.edad_minima is None else edad > self.edad_minima
                    cumple_maximo = True if self.edad_maxima is None else edad < self.edad_maxima
                    
                    if cumple_minimo and cumple_maximo:
                        clientes_filtrados.append(cliente)
            
            clientes = clientes_filtrados
        
        # Actualizar tabla con clientes filtrados
        self.tabla.setRowCount(len(clientes))
        
        for i, cliente in enumerate(clientes):
            # Nombre
            self.tabla.setItem(i, 0, QTableWidgetItem(cliente['nombre']))
            
            # Teléfono
            self.tabla.setItem(i, 1, QTableWidgetItem(cliente['telefono'] or "-"))
            
            # Edad
            fecha_nac = cliente.get('fecha_nacimiento', '')
            if fecha_nac:
                fecha = date.fromisoformat(fecha_nac)
                hoy = date.today()
                edad = hoy.year - fecha.year - ((hoy.month, hoy.day) < (fecha.month, fecha.day))
                self.tabla.setItem(i, 2, QTableWidgetItem(str(edad)))
            else:
                self.tabla.setItem(i, 2, QTableWidgetItem("-"))
            
            # Sexo
            self.tabla.setItem(i, 3, QTableWidgetItem(cliente.get('sexo', "-")))
            
            # Fecha de nacimiento
            if fecha_nac:
                fecha_texto = fecha.strftime("%d/%m/%Y")
            else:
                fecha_texto = "-"
            self.tabla.setItem(i, 4, QTableWidgetItem(fecha_texto))
            
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
            btn_editar.clicked.connect(lambda checked, c=cliente: self.editar_cliente(c))
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
            btn_eliminar.clicked.connect(lambda checked, cid=cliente['id']: self.eliminar_cliente(cid))
            acciones_layout.addWidget(btn_eliminar)
            
            self.tabla.setCellWidget(i, 5, acciones_widget)
