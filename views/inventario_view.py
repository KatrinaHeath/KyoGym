"""Vista de gestión de inventario"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QTableWidget, QTableWidgetItem, QHeaderView, QLabel,
                               QDialog, QFormLayout, QLineEdit, QComboBox,
                               QMessageBox, QDialogButtonBox, QSpinBox, QDoubleSpinBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from services import inventario_service


class AgregarProductoDialog(QDialog):
    """Diálogo para agregar/editar producto"""
    def __init__(self, parent=None, producto=None):
        super().__init__(parent)
        self.producto = producto
        self.setWindowTitle("Editar Producto" if producto else "Nuevo Producto")
        self.setMinimumWidth(400)
        self.init_ui()
        
        if producto:
            self.cargar_datos_producto()
    
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
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                padding: 8px;
                border: 2px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
                color: #2c3e50;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border: 2px solid #3498db;
            }
            QPushButton {
                color: black;
            }
        """)
        
        # Nombre
        self.nombre = QLineEdit()
        self.nombre.setPlaceholderText("Ingrese el nombre del producto")
        layout.addRow("Nombre:", self.nombre)
        
        # Categoría
        self.categoria = QComboBox()
        self.categoria.setEditable(True)
        categorias_existentes = inventario_service.obtener_categorias()
        self.categoria.addItems(["Suplementos", "Equipamiento", "Accesorios", "Bebidas", "Otros"])
        if categorias_existentes:
            for cat in categorias_existentes:
                if cat not in ["Suplementos", "Equipamiento", "Accesorios", "Bebidas", "Otros"]:
                    self.categoria.addItem(cat)
        layout.addRow("Categoría:", self.categoria)
        
        # Cantidad
        self.cantidad = QSpinBox()
        self.cantidad.setMinimum(0)
        self.cantidad.setMaximum(999999)
        self.cantidad.setValue(0)
        layout.addRow("Cantidad:", self.cantidad)
        
        # Precio
        self.precio = QDoubleSpinBox()
        self.precio.setMinimum(0.0)
        self.precio.setMaximum(999999.99)
        self.precio.setDecimals(2)
        self.precio.setPrefix("$")
        self.precio.setValue(0.0)
        layout.addRow("Precio:", self.precio)
        
        # Botones
        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botones.accepted.connect(self.aceptar)
        botones.rejected.connect(self.reject)
        layout.addRow(botones)
        
        self.setLayout(layout)
    
    def cargar_datos_producto(self):
        """Carga los datos del producto para editar"""
        self.nombre.setText(self.producto['nombre'])
        self.categoria.setCurrentText(self.producto['categoria'])
        self.cantidad.setValue(self.producto['cantidad'])
        self.precio.setValue(self.producto['precio'])
    
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
        
        if not self.categoria.currentText().strip():
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setText("La categoría es requerida")
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
        return {
            'nombre': self.nombre.text().strip(),
            'categoria': self.categoria.currentText().strip(),
            'cantidad': self.cantidad.value(),
            'precio': self.precio.value()
        }


class InventarioView(QWidget):
    """Vista de gestión de inventario"""
    def __init__(self):
        super().__init__()
        self.filtro_categoria = None
        self.init_ui()
        self.cargar_datos()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Encabezado
        header_layout = QHBoxLayout()
        
        titulo = QLabel("Inventario")
        titulo.setFont(QFont("Arial", 24, QFont.Bold))
        titulo.setStyleSheet("color: #000000;")
        header_layout.addWidget(titulo)
        
        header_layout.addStretch()
        
        # Búsqueda
        self.buscar_input = QLineEdit()
        self.buscar_input.setPlaceholderText("Buscar producto...")
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
        
        btn_agregar = QPushButton("Agregar Producto")
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
        btn_agregar.clicked.connect(self.agregar_producto)
        header_layout.addWidget(btn_agregar)
        
        layout.addLayout(header_layout)
        
        # Filtros por categoría
        filtros_layout = QHBoxLayout()
        
        label_categoria = QLabel("Categoría:")
        label_categoria.setStyleSheet("color: #000000; font-weight: bold;")
        filtros_layout.addWidget(label_categoria)
        
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
        
        self.btn_todas_categorias = QPushButton("Todas")
        self.btn_todas_categorias.setCheckable(True)
        self.btn_todas_categorias.setChecked(True)
        self.btn_todas_categorias.clicked.connect(lambda: self.cambiar_filtro_categoria(None, self.btn_todas_categorias))
        self.btn_todas_categorias.setStyleSheet(estilo_botones)
        filtros_layout.addWidget(self.btn_todas_categorias)
        
        # Botones de categorías comunes
        self.botones_categoria = {}
        categorias_comunes = ["Suplementos", "Equipamiento", "Accesorios", "Bebidas"]
        
        for cat in categorias_comunes:
            btn = QPushButton(cat)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, c=cat, b=btn: self.cambiar_filtro_categoria(c, b))
            btn.setStyleSheet(estilo_botones)
            filtros_layout.addWidget(btn)
            self.botones_categoria[cat] = btn
        
        filtros_layout.addStretch()
        
        layout.addLayout(filtros_layout)
        
        # Tabla de inventario
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(["Nombre", "Categoría", "Cantidad", "Precio", "Valor Total", "Acciones"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setAlternatingRowColors(False)
        self.tabla.verticalHeader().setVisible(False)
        
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
                color: white;
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
    
    def cargar_datos(self):
        """Carga los productos en la tabla"""
        buscar = self.buscar_input.text() if hasattr(self, 'buscar_input') else ""
        productos = inventario_service.listar_productos(buscar=buscar, categoria=self.filtro_categoria)
        
        self.tabla.setRowCount(len(productos))
        
        for i, producto in enumerate(productos):
            # Nombre
            self.tabla.setItem(i, 0, QTableWidgetItem(producto['nombre']))
            
            # Categoría
            self.tabla.setItem(i, 1, QTableWidgetItem(producto['categoria']))
            
            # Cantidad
            cantidad_item = QTableWidgetItem(str(producto['cantidad']))
            # Colorear según stock
            if producto['cantidad'] == 0:
                cantidad_item.setForeground(QColor("#e74c3c"))  # Rojo
            elif producto['cantidad'] < 5:
                cantidad_item.setForeground(QColor("#f39c12"))  # Naranja
            else:
                cantidad_item.setForeground(QColor("#27ae60"))  # Verde
            self.tabla.setItem(i, 2, cantidad_item)
            
            # Precio
            precio_item = QTableWidgetItem(f"${producto['precio']:.2f}")
            self.tabla.setItem(i, 3, precio_item)
            
            # Valor Total
            valor_total = producto['cantidad'] * producto['precio']
            valor_item = QTableWidgetItem(f"${valor_total:.2f}")
            valor_item.setForeground(QColor("#27ae60"))
            self.tabla.setItem(i, 4, valor_item)
            
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
            btn_editar.clicked.connect(lambda checked, p=producto: self.editar_producto(p))
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
            btn_eliminar.clicked.connect(lambda checked, pid=producto['id']: self.eliminar_producto(pid))
            acciones_layout.addWidget(btn_eliminar)
            
            self.tabla.setCellWidget(i, 5, acciones_widget)
    
    def cambiar_filtro_categoria(self, categoria, boton_activo):
        """Cambia el filtro de categoría"""
        # Desmarcar todos los botones
        self.btn_todas_categorias.setChecked(False)
        for btn in self.botones_categoria.values():
            btn.setChecked(False)
        
        # Marcar el botón activo
        boton_activo.setChecked(True)
        
        # Actualizar filtro
        self.filtro_categoria = categoria
        self.cargar_datos()
    
    def agregar_producto(self):
        """Muestra diálogo para agregar producto"""
        dialog = AgregarProductoDialog(self)
        if dialog.exec():
            datos = dialog.obtener_datos()
            try:
                inventario_service.crear_producto(
                    nombre=datos['nombre'],
                    categoria=datos['categoria'],
                    cantidad=datos['cantidad'],
                    precio=datos['precio']
                )
                
                msg = QMessageBox(self)
                msg.setWindowTitle("Éxito")
                msg.setText("Producto agregado exitosamente")
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
                msg.setText(f"Error al agregar producto: {str(e)}")
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
    
    def editar_producto(self, producto):
        """Muestra diálogo para editar producto"""
        dialog = AgregarProductoDialog(self, producto)
        if dialog.exec():
            datos = dialog.obtener_datos()
            try:
                inventario_service.actualizar_producto(
                    producto_id=producto['id'],
                    nombre=datos['nombre'],
                    categoria=datos['categoria'],
                    cantidad=datos['cantidad'],
                    precio=datos['precio']
                )
                
                msg = QMessageBox(self)
                msg.setWindowTitle("Éxito")
                msg.setText("Producto actualizado exitosamente")
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
                msg.setText(f"Error al actualizar producto: {str(e)}")
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
    
    def eliminar_producto(self, producto_id):
        """Elimina un producto"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Confirmar eliminación")
        msg.setText("¿Está seguro de eliminar este producto?")
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
                inventario_service.eliminar_producto(producto_id)
                
                msg = QMessageBox(self)
                msg.setWindowTitle("Éxito")
                msg.setText("Producto eliminado exitosamente")
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
                msg.setText(f"Error al eliminar producto: {str(e)}")
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

