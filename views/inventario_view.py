"""Vista de inventario con CRUD básico y diálogo para agregar artículos"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QTableWidget, QTableWidgetItem, QHeaderView, QLabel,
                               QDialog, QFormLayout, QLineEdit, QSpinBox, QDoubleSpinBox,
                               QMessageBox, QDialogButtonBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from services import inventario_service


class AgregarArticuloDialog(QDialog):
    """Diálogo para agregar/editar artículo de inventario"""
    def __init__(self, parent=None, articulo=None):
        super().__init__(parent)
        self.articulo = articulo
        self.setWindowTitle("Editar Artículo" if articulo else "Agregar Artículo")
        self.setMinimumWidth(380)
        self.init_ui()

        if articulo:
            self.cargar_datos()

    def init_ui(self):
        layout = QFormLayout()

        # Forzar estilos locales en el diálogo para asegurar contraste
        self.setStyleSheet("""
            QDialog { background-color: white; }
            QLabel { color: #2c3e50; font-size: 13px; }
            QLineEdit, QComboBox, QDateEdit, QSpinBox, QAbstractSpinBox {
                padding: 8px;
                border: 2px solid #e0e0e0;
                border-radius: 4px;
                background-color: white;
                color: #2c3e50;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QAbstractSpinBox:focus {
                border: 2px solid #3498db;
            }
            QDialogButtonBox QPushButton {
                padding: 6px 12px;
                border-radius: 4px;
                background-color: #f0f0f0;
                color: #2c3e50;
            }
            QDialogButtonBox QPushButton:disabled {
                color: #9b9b9b;
                background-color: #f7f7f7;
            }
        """)

        self.nombre = QLineEdit()
        self.nombre.setPlaceholderText("Nombre del artículo")
        layout.addRow("Nombre:", self.nombre)

        self.categoria = QLineEdit()
        self.categoria.setPlaceholderText("Categoría (Ej: Equipos, Suplementos)")
        layout.addRow("Categoría:", self.categoria)

        self.cantidad = QSpinBox()
        self.cantidad.setRange(0, 1000000)
        layout.addRow("Cantidad:", self.cantidad)

        self.precio = QDoubleSpinBox()
        self.precio.setRange(0, 1000000)
        self.precio.setDecimals(2)
        self.precio.setPrefix("$")
        layout.addRow("Precio:", self.precio)

        # Botones
        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botones.accepted.connect(self.aceptar)
        botones.rejected.connect(self.reject)
        layout.addRow(botones)

        self.setLayout(layout)

    def cargar_datos(self):
        self.nombre.setText(self.articulo.get('nombre', ''))
        self.categoria.setText(self.articulo.get('categoria', ''))
        self.cantidad.setValue(int(self.articulo.get('cantidad', 0)))
        # Precio puede venir como None o 0.0
        try:
            self.precio.setValue(float(self.articulo.get('precio', 0.0)))
        except Exception:
            self.precio.setValue(0.0)

    def aceptar(self):
        if not self.nombre.text().strip():
            QMessageBox.warning(self, "Error", "El nombre es requerido")
            return
        self.accept()

    def obtener_datos(self):
        return {
            'nombre': self.nombre.text().strip(),
            'categoria': self.categoria.text().strip(),
            'cantidad': int(self.cantidad.value()),
            'precio': float(self.precio.value())
        }


class InventarioView(QWidget):
    """Vista de gestión de inventario"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.cargar_datos()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Encabezado
        header_layout = QHBoxLayout()

        titulo = QLabel("Inventario")
        titulo.setFont(QFont("Arial", 24, QFont.Bold))
        titulo.setStyleSheet("color: #000000;")
        header_layout.addWidget(titulo)

        header_layout.addStretch()

        # Búsqueda
        from PySide6.QtWidgets import QLineEdit
        self.buscar_input = QLineEdit()
        self.buscar_input.setPlaceholderText("Buscar artículos...")
        self.buscar_input.setMinimumWidth(300)
        self.buscar_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                font-size: 13px;
                color: #2c3e50;
            }
        """)
        self.buscar_input.textChanged.connect(self.cargar_datos)
        header_layout.addWidget(self.buscar_input)

        btn_agregar = QPushButton("Agregar Artículo")
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
        btn_agregar.clicked.connect(self.agregar_articulo)
        header_layout.addWidget(btn_agregar)

        layout.addLayout(header_layout)

        # Tabla de inventario
        self.tabla = QTableWidget()
        # Columnas: ID, Nombre, Categoría, Cantidad, Precio, Acciones
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "Categoría", "Cantidad", "Precio", "Acciones"])

        self.tabla.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
        """)

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

        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        self.tabla.setColumnWidth(5, 200)

        layout.addWidget(self.tabla)

        # Pie (paginación simulada)
        footer_layout = QHBoxLayout()
        self.paginacion_label = QLabel("")
        footer_layout.addWidget(self.paginacion_label)
        footer_layout.addStretch()
        layout.addLayout(footer_layout)

        self.setLayout(layout)

    def cargar_datos(self):
        buscar = self.buscar_input.text() if hasattr(self, 'buscar_input') else ""
        articulos = inventario_service.listar_articulos(buscar=buscar)

        self.tabla.setRowCount(len(articulos))

        for i, art in enumerate(articulos):
            # ID
            id_item = QTableWidgetItem(str(art.get('id', '')))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(i, 0, id_item)

            self.tabla.setItem(i, 1, QTableWidgetItem(art.get('nombre', '-')))
            self.tabla.setItem(i, 2, QTableWidgetItem(art.get('categoria', '-') or '-'))

            cantidad_item = QTableWidgetItem(str(art.get('cantidad', 0)))
            cantidad_item.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(i, 3, cantidad_item)
            precio_val = art.get('precio', 0.0) or 0.0
            try:
                precio_txt = f"${float(precio_val):,.2f}"
            except Exception:
                precio_txt = str(precio_val)
            precio_item = QTableWidgetItem(precio_txt)
            precio_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabla.setItem(i, 4, precio_item)

            acciones_widget = QWidget()
            acciones_layout = QHBoxLayout(acciones_widget)
            acciones_layout.setContentsMargins(5, 0, 5, 0)
            acciones_layout.setSpacing(8)

            btn_editar = QPushButton("Editar")
            btn_editar.setStyleSheet("""
                QPushButton { background-color: #3498db; color: white; padding: 5px 12px; border: none; border-radius: 3px; }
                QPushButton:hover { background-color: #2980b9; }
            """)
            btn_editar.clicked.connect(lambda checked, a=art: self.editar_articulo(a))
            acciones_layout.addWidget(btn_editar)

            btn_eliminar = QPushButton("Eliminar")
            btn_eliminar.setStyleSheet("""
                QPushButton { background-color: #e74c3c; color: white; padding: 5px 12px; border: none; border-radius: 3px; }
                QPushButton:hover { background-color: #c0392b; }
            """)
            btn_eliminar.clicked.connect(lambda checked, aid=art['id']: self.eliminar_articulo(aid))
            acciones_layout.addWidget(btn_eliminar)

            # Colocar las acciones en la última columna
            self.tabla.setCellWidget(i, 5, acciones_widget)

        # Actualizar etiqueta de paginación/simple conteo
        total = len(articulos)
        self.paginacion_label.setText(f"1 a {total} de {total}")

    def agregar_articulo(self):
        dialog = AgregarArticuloDialog(self)
        # Pre-fill con ejemplo de prueba para facilitar pruebas
        dialog.nombre.setText("Mancuernas")
        dialog.categoria.setText("Equipos")
        dialog.cantidad.setValue(20)
        dialog.precio.setValue(120.00)

        if dialog.exec() == QDialog.Accepted:
            datos = dialog.obtener_datos()
            try:
                inventario_service.crear_articulo(
                    nombre=datos['nombre'],
                    categoria=datos['categoria'],
                    cantidad=datos['cantidad'],
                    precio=datos.get('precio', 0.0)
                )
                # Usar cuadro de mensaje con estilo para asegurar visibilidad
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Éxito")
                msg.setText("Artículo agregado exitosamente")
                msg.setStyleSheet("QLabel{ color: #2c3e50; } QPushButton{ padding:6px 12px; }")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
                self.cargar_datos()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al agregar artículo: {str(e)}")

    def editar_articulo(self, articulo):
        dialog = AgregarArticuloDialog(self, articulo)
        if dialog.exec() == QDialog.Accepted:
            datos = dialog.obtener_datos()
            try:
                inventario_service.actualizar_articulo(
                    articulo_id=articulo['id'],
                    nombre=datos['nombre'],
                    categoria=datos['categoria'],
                    cantidad=datos['cantidad'],
                    precio=datos.get('precio', 0.0)
                )
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Éxito")
                msg.setText("Artículo actualizado exitosamente")
                msg.setStyleSheet("QLabel{ color: #2c3e50; } QPushButton{ padding:6px 12px; }")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
                self.cargar_datos()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al actualizar artículo: {str(e)}")

    def eliminar_articulo(self, articulo_id):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle("Confirmar eliminación")
        msg.setText("¿Está seguro de eliminar este artículo?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setStyleSheet("QLabel{ color: #2c3e50; } QPushButton{ color: #2c3e50; padding:6px 12px; } QPushButton:hover{ background-color: #f0f0f0; }")
        respuesta = msg.exec()

        if respuesta == QMessageBox.Yes:
            try:
                inventario_service.eliminar_articulo(articulo_id)
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Éxito")
                msg.setText("Artículo eliminado exitosamente")
                msg.setStyleSheet("QLabel{ color: #2c3e50; } QPushButton{ padding:6px 12px; }")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
                self.cargar_datos()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al eliminar artículo: {str(e)}")
