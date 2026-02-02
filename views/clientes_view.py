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
            QMessageBox.warning(self, "Error", "El nombre es requerido")
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
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        btn_agregar.clicked.connect(self.agregar_cliente)
        header_layout.addWidget(btn_agregar)
        
        layout.addLayout(header_layout)
        
        # Tabla de clientes
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "Teléfono", "Sexo", "Fecha Nacimiento", "Acciones"])
        self.tabla.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
        """)
        
        # Configurar tabla
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f8f9fa;
                gridline-color: #e0e0e0;
                border: 1px solid #e0e0e0;
            }
            QTableWidget::item {
                padding: 8px;
                color: #2c3e50;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        
        # Ajustar columnas
        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        self.tabla.setColumnWidth(0, 50)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        self.tabla.setColumnWidth(5, 180)
        
        layout.addWidget(self.tabla)
        
        self.setLayout(layout)
    
    def cargar_datos(self):
        """Carga los clientes en la tabla"""
        buscar = self.buscar_input.text() if hasattr(self, 'buscar_input') else ""
        clientes = cliente_service.listar_clientes(buscar=buscar)
        
        self.tabla.setRowCount(len(clientes))
        
        for i, cliente in enumerate(clientes):
            # ID
            self.tabla.setItem(i, 0, QTableWidgetItem(str(cliente['id'])))
            
            # Nombre
            self.tabla.setItem(i, 1, QTableWidgetItem(cliente['nombre']))
            
            # Teléfono
            self.tabla.setItem(i, 2, QTableWidgetItem(cliente['telefono'] or "-"))
            
            # Sexo
            self.tabla.setItem(i, 3, QTableWidgetItem(cliente.get('sexo', "-")))
            
            # Fecha de nacimiento
            fecha_nac = cliente.get('fecha_nacimiento', '')
            if fecha_nac:
                fecha = date.fromisoformat(fecha_nac)
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
                }
                QPushButton:hover {
                    background-color: #2980b9;
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
                }
                QPushButton:hover {
                    background-color: #c0392b;
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
                cliente_service.crear_cliente(
                    nombre=datos['nombre'],
                    telefono=datos['telefono'],
                    sexo=datos['sexo'],
                    fecha_nacimiento=datos['fecha_nacimiento']
                )
                QMessageBox.information(self, "Éxito", "Cliente agregado exitosamente")
                self.cargar_datos()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al agregar cliente: {str(e)}")
    
    def editar_cliente(self, cliente):
        """Muestra diálogo para editar cliente"""
        dialog = AgregarClienteDialog(self, cliente)
        if dialog.exec() == QDialog.Accepted:
            datos = dialog.obtener_datos()
            try:
                cliente_service.actualizar_cliente(
                    cliente_id=cliente['id'],
                    nombre=datos['nombre'],
                    telefono=datos['telefono'],
                    sexo=datos['sexo'],
                    fecha_nacimiento=datos['fecha_nacimiento']
                )
                QMessageBox.information(self, "Éxito", "Cliente actualizado exitosamente")
                self.cargar_datos()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al actualizar cliente: {str(e)}")
    
    def eliminar_cliente(self, cliente_id):
        """Elimina un cliente"""
        respuesta = QMessageBox.question(
            self,
            "Confirmar eliminación",
            "¿Está seguro de eliminar este cliente?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if respuesta == QMessageBox.Yes:
            try:
                cliente_service.eliminar_cliente(cliente_id)
                QMessageBox.information(self, "Éxito", "Cliente eliminado exitosamente")
                self.cargar_datos()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al eliminar cliente: {str(e)}")
