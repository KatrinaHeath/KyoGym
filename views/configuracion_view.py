"""Vista de configuración del sistema"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QFrame, QLineEdit, QPushButton, QGroupBox,
                               QFormLayout, QComboBox, QSpinBox, QCheckBox, QDialog,
                               QMessageBox, QScrollArea, QFileDialog,
                               QTableWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap
from utils.validators import crear_validador_nombre, TelefonoFormateadoLineEdit, crear_validador_email
from usuario_activo import obtener_usuario_activo
from db import create_user, get_all_users, delete_user
import json
import os


DEFAULT_DIAS_ALERTA_VENCIMIENTO = 7


class VerUsuariosDialog(QDialog):
    """Diálogo que lista todos los usuarios con opción de eliminar por fila."""

    def __init__(self, usuario_activo="", parent=None):
        super().__init__(parent)
        self.usuario_activo = usuario_activo
        self.setWindowTitle("Usuarios del sistema")
        self.setMinimumSize(580, 380)
        self._init_ui()
        self._cargar()

    def _init_ui(self):
        self.setStyleSheet("""
            QDialog { background-color: white; }
            QLabel { color: #2c3e50; font-size: 13px; border: none; background: transparent; }
            QTableWidget {
                border: 2px solid #000000; border-radius: 5px;
                gridline-color: #e0e0e0; font-size: 13px; color: #000;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #2c3e50; color: white;
                font-weight: bold; font-size: 13px;
                padding: 6px; border: none;
            }
            QPushButton#btn_cerrar {
                background-color: #7f8c8d; color: white;
                padding: 8px 20px; border: none;
                border-radius: 4px; font-weight: bold; font-size: 13px;
            }
            QPushButton#btn_cerrar:hover { background-color: #636e72; }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        titulo = QLabel("Usuarios registrados")
        titulo.setFont(QFont("Arial", 15, QFont.Bold))
        titulo.setStyleSheet("color: #2c3e50; margin-bottom: 4px; border: none; background: transparent;")
        layout.addWidget(titulo)

        self.tabla = QTableWidget(0, 4)
        self.tabla.setHorizontalHeaderLabels(["Nombre completo", "Usuario", "Rol", "Acción"])
        self.tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.tabla.setColumnWidth(3, 110)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionMode(QTableWidget.NoSelection)
        self.tabla.verticalHeader().setVisible(False)
        layout.addWidget(self.tabla)

        btn_layout = QHBoxLayout()
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setObjectName("btn_cerrar")
        btn_cerrar.clicked.connect(self.accept)
        btn_layout.addWidget(btn_cerrar)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def _cargar(self):
        usuarios = get_all_users()
        self.tabla.setRowCount(len(usuarios))
        for row, u in enumerate(usuarios):
            username = u['username']
            self.tabla.setItem(row, 0, QTableWidgetItem(u.get('full_name') or username))
            self.tabla.setItem(row, 1, QTableWidgetItem(username))
            self.tabla.setItem(row, 2, QTableWidgetItem(u['role']))

            btn_del = QPushButton("🗑️ Eliminar")
            btn_del.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c; color: white;
                    padding: 4px 10px; border: none;
                    border-radius: 4px; font-weight: bold; font-size: 12px;
                    margin: 2px;
                }
                QPushButton:hover { background-color: #c0392b; }
                QPushButton:disabled { background-color: #bdc3c7; color: #888; }
            """)
            if username == self.usuario_activo:
                btn_del.setEnabled(False)
                btn_del.setToolTip("No puedes eliminar tu propio usuario")
            else:
                btn_del.clicked.connect(lambda checked, usr=username: self._confirmar_eliminar(usr))
            self.tabla.setCellWidget(row, 3, btn_del)

    def _confirmar_eliminar(self, username):
        msg = QMessageBox(self)
        msg.setWindowTitle("Confirmar")
        msg.setText(f"¿Eliminar el usuario \'{username}\'?\nEsta acción no se puede deshacer.")
        msg.setStyleSheet("""
            QMessageBox { background-color: white; }
            QLabel { color: black; font-size: 14px; min-width: 280px; border: none; }
            QPushButton {
                background-color: #2c3e50; color: white;
                padding: 8px 20px; border: none;
                border-radius: 4px; font-weight: bold;
                font-size: 13px; min-width: 70px;
            }
            QPushButton:hover { background-color: #3d5166; }
        """)
        btn_si = msg.addButton("Sí", QMessageBox.YesRole)
        btn_no = msg.addButton("No", QMessageBox.NoRole)
        msg.setDefaultButton(btn_no)
        msg.exec()
        if msg.clickedButton() != btn_si:
            return
        ok = delete_user(username)
        if ok:
            self._cargar()
        else:
            QMessageBox.critical(self, "Error", "No se pudo eliminar el usuario.")


class CrearUsuarioDialog(QDialog):
    """Diálogo para crear un nuevo usuario del sistema."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Crear nuevo usuario")
        self.setMinimumWidth(420)
        self._init_ui()

    def _init_ui(self):
        self.setStyleSheet("""
            QDialog { background-color: white; }
            QLabel { color: #2c3e50; font-size: 13px; }
            QLineEdit, QComboBox {
                padding: 7px; font-size: 13px; color: #000;
                border: 2px solid #000000; border-radius: 5px;
                background-color: white;
            }
            QPushButton {
                background-color: #27ae60; color: white;
                padding: 10px 24px; border: none;
                border-radius: 5px; font-weight: bold; font-size: 13px;
            }
            QPushButton:hover { background-color: #229954; }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        titulo = QLabel("Nuevo usuario")
        titulo.setFont(QFont("Arial", 15, QFont.Bold))
        titulo.setStyleSheet("color: #2c3e50; margin-bottom: 6px;")
        layout.addWidget(titulo)

        form = QFormLayout()
        form.setSpacing(10)

        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("Nombre de usuario")
        form.addRow("Usuario:", self.txt_username)

        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("Nombre completo (opcional)")
        form.addRow("Nombre completo:", self.txt_nombre)

        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setPlaceholderText("Contraseña")
        form.addRow("Contraseña:", self.txt_password)

        self.txt_password2 = QLineEdit()
        self.txt_password2.setEchoMode(QLineEdit.Password)
        self.txt_password2.setPlaceholderText("Repetir contraseña")
        form.addRow("Confirmar:", self.txt_password2)

        self.cmb_rol = QComboBox()
        self.cmb_rol.addItems(["user", "admin"])
        self.cmb_rol.setEditable(False)
        form.addRow("Rol:", self.cmb_rol)

        layout.addLayout(form)

        btn_crear = QPushButton("➕ Crear usuario")
        btn_crear.clicked.connect(self._crear)
        layout.addWidget(btn_crear)

    def _crear(self):
        username = self.txt_username.text().strip()
        nombre = self.txt_nombre.text().strip() or username
        password = self.txt_password.text()
        password2 = self.txt_password2.text()
        role = self.cmb_rol.currentText()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Usuario y contraseña son obligatorios.")
            return
        if password != password2:
            QMessageBox.warning(self, "Error", "Las contraseñas no coinciden.")
            return

        ok = create_user(username, password, full_name=nombre, role=role)
        if ok:
            QMessageBox.information(self, "Éxito",
                f"Usuario \'{username}\' creado correctamente con rol \'{role}\'.")
            self.accept()
        else:
            QMessageBox.critical(self, "Error",
                "No se pudo crear el usuario. Es posible que ya exista.")


class ConfiguracionView(QWidget):
    """Vista de configuración del sistema"""
    logout_solicitado = Signal()

    def __init__(self):
        super().__init__()
        self.config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
        self.logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")
        self._usuario_activo = ""
        self.init_ui()
        self.cargar_configuracion()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        # Layout principal con scroll
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Área con scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #f5f6fa; }")
        
        # Widget contenedor
        container = QWidget()
        scroll.setWidget(container)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Título
        titulo = QLabel("⚙️ Configuración del Sistema")
        titulo.setFont(QFont("Arial", 24, QFont.Bold))
        titulo.setStyleSheet("color: #2c3e50; background-color: transparent;")
        layout.addWidget(titulo)
        
        # Separador
        separador = QFrame()
        separador.setFrameShape(QFrame.HLine)
        separador.setStyleSheet("background-color: #bdc3c7;")
        layout.addWidget(separador)
        
        # Información del Gimnasio
        layout.addWidget(self.crear_grupo_gimnasio())
        
        # Logo del Gimnasio
        layout.addWidget(self.crear_grupo_logo())
        
        # Configuración de Notificaciones
        layout.addWidget(self.crear_grupo_notificaciones())
        
        # Configuración de Facturas
        layout.addWidget(self.crear_grupo_facturas())

        # Gestión de Usuarios (solo admin / prueba)
        self._grupo_usuarios = self._crear_grupo_usuarios()
        self._grupo_usuarios.setVisible(False)
        layout.addWidget(self._grupo_usuarios)

        # Botones de acción
        botones_layout = QHBoxLayout()
        
        btn_guardar = QPushButton("💾 Guardar Configuración")
        btn_guardar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
                color: white;
            }
        """)
        btn_guardar.clicked.connect(self.guardar_configuracion)
        
        btn_reset = QPushButton("🔄 Restaurar Valores Predeterminados")
        btn_reset.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
                color: white;
            }
        """)
        btn_reset.clicked.connect(self.restaurar_predeterminados)
        
        botones_layout.addWidget(btn_guardar)
        botones_layout.addWidget(btn_reset)
        # Botón para cerrar sesión
        btn_cerrar = QPushButton("🔒 Cerrar sesión")
        btn_cerrar.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
                color: white;
            }
        """)
        btn_cerrar.clicked.connect(self.cerrar_sesion)
        botones_layout.addWidget(btn_cerrar)
        botones_layout.addStretch()
        
        layout.addLayout(botones_layout)
        layout.addStretch()
        
        main_layout.addWidget(scroll)
        
        # Forzar color negro global en QLabel para mejor legibilidad
        self.setStyleSheet("""
            QLabel {
                color: #000000;
            }
        """)
    
    def _crear_grupo_usuarios(self):
        """Crea el grupo de gestión de usuarios."""
        grupo = QGroupBox("👥 Gestión de Usuarios")
        grupo.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #000000;
                background-color: white;
                border: 2px solid #000000;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        layout = QVBoxLayout(grupo)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        lbl = QLabel("Administra los usuarios que pueden acceder al sistema.")
        lbl.setStyleSheet("color: #555; font-size: 13px;")
        layout.addWidget(lbl)

        btns_layout = QHBoxLayout()

        btn_crear = QPushButton("➕ Crear nuevo usuario")
        btn_crear.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2471a3; }
        """)
        btn_crear.clicked.connect(self._abrir_crear_usuario)
        btns_layout.addWidget(btn_crear)

        btn_ver = QPushButton("👥 Ver usuarios")
        btn_ver.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #229954; }
        """)
        btn_ver.clicked.connect(self._abrir_ver_usuarios)
        btns_layout.addWidget(btn_ver)
        btns_layout.addStretch()

        layout.addLayout(btns_layout)
        return grupo

    def _abrir_crear_usuario(self):
        """Abre el diálogo para crear un usuario."""
        dialog = CrearUsuarioDialog(self)
        dialog.exec()

    def _abrir_ver_usuarios(self):
        """Abre el diálogo para ver y eliminar usuarios."""
        dialog = VerUsuariosDialog(usuario_activo=self._usuario_activo, parent=self)
        dialog.exec()

    def set_usuario(self, username: str, role: str):
        """Muestra u oculta la sección de usuarios según el rol."""
        self._usuario_activo = username
        es_privilegiado = role == 'admin' or username == 'prueba'
        self._grupo_usuarios.setVisible(es_privilegiado)

    def crear_grupo_gimnasio(self):
        """Crea el grupo de información del gimnasio"""
        grupo = QGroupBox("📋 Información del Gimnasio")
        grupo.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #000000;
                background-color: white;
                border: 2px solid #000000;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)
        
        layout = QFormLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 25, 20, 20)
        
        # Nombre del gimnasio
        self.txt_nombre_gym = QLineEdit()
        self.txt_nombre_gym.setPlaceholderText("Ej: KyoGym")
        self.txt_nombre_gym.setValidator(crear_validador_nombre())
        self.aplicar_estilo_input(self.txt_nombre_gym)
        
        # Dirección
        self.txt_direccion = QLineEdit()
        self.txt_direccion.setPlaceholderText("Ej: Calle Principal #123")
        self.aplicar_estilo_input(self.txt_direccion)
        
        # Teléfono
        self.txt_telefono = TelefonoFormateadoLineEdit()
        self.aplicar_estilo_input(self.txt_telefono)
        
        # Email
        self.txt_email = QLineEdit()
        self.txt_email.setPlaceholderText("Ej: info@kyogym.com")
        self.txt_email.setValidator(crear_validador_email())
        self.aplicar_estilo_input(self.txt_email)
        
        # RFC/NIT
        self.txt_rfc = QLineEdit()
        self.txt_rfc.setPlaceholderText("Ej: ABC123456XYZ")
        self.aplicar_estilo_input(self.txt_rfc)
        
        layout.addRow("Nombre:", self.txt_nombre_gym)
        layout.addRow("Dirección:", self.txt_direccion)
        layout.addRow("Teléfono:", self.txt_telefono)
        layout.addRow("Email:", self.txt_email)
        layout.addRow("RFC/NIT:", self.txt_rfc)
        
        grupo.setLayout(layout)
        return grupo
    
    def crear_grupo_logo(self):
        """Crea el grupo de logo del gimnasio"""
        grupo = QGroupBox("🖼️ Logo del Gimnasio")
        grupo.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #000000;
                background-color: white;
                border: 2px solid #000000;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 25, 20, 20)
        
        # Preview del logo
        preview_layout = QHBoxLayout()
        
        self.logo_preview = QLabel()
        self.logo_preview.setFixedSize(120, 120)
        self.logo_preview.setStyleSheet("""
            border: 2px dashed #bdc3c7;
            background-color: #ecf0f1;
            border-radius: 8px;
        """)
        self.logo_preview.setAlignment(Qt.AlignCenter)
        self.actualizar_preview_logo()
        
        preview_layout.addWidget(self.logo_preview)
        
        # Botones de logo
        botones_logo = QVBoxLayout()
        
        btn_cambiar_logo = QPushButton("📁 Seleccionar Logo")
        btn_cambiar_logo.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
                color: white;
            }
        """)
        btn_cambiar_logo.clicked.connect(self.seleccionar_logo)
        
        btn_eliminar_logo = QPushButton("🗑️ Eliminar Logo")
        btn_eliminar_logo.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
                color: white;
            }
        """)
        btn_eliminar_logo.clicked.connect(self.eliminar_logo)
        
        botones_logo.addWidget(btn_cambiar_logo)
        botones_logo.addWidget(btn_eliminar_logo)
        botones_logo.addStretch()
        
        preview_layout.addLayout(botones_logo)
        preview_layout.addStretch()
        
        layout.addLayout(preview_layout)
        
        info_label = QLabel("Formatos soportados: PNG, JPG, ICO. Tamaño recomendado: 200x200px")
        info_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        layout.addWidget(info_label)
        
        grupo.setLayout(layout)
        return grupo
    
    def crear_grupo_notificaciones(self):
        """Crea el grupo de notificaciones"""
        grupo = QGroupBox("🔔 Notificaciones")
        grupo.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #000000;
                background-color: white;
                border: 2px solid #000000;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 25, 20, 20)
        
        # Checkboxes para notificaciones
        self.chk_notif_vencimiento = QCheckBox("Alertas de vencimiento de membresías")
        self.chk_notif_vencimiento.setChecked(True)
        self.aplicar_estilo_checkbox(self.chk_notif_vencimiento)
        
        self.chk_notif_pagos = QCheckBox("Confirmación de pagos recibidos")
        self.chk_notif_pagos.setChecked(True)
        self.aplicar_estilo_checkbox(self.chk_notif_pagos)
        
        self.chk_notif_nuevos = QCheckBox("Nuevos clientes registrados")
        self.chk_notif_nuevos.setChecked(True)
        self.aplicar_estilo_checkbox(self.chk_notif_nuevos)
        
        layout.addWidget(self.chk_notif_vencimiento)
        layout.addWidget(self.chk_notif_pagos)
        layout.addWidget(self.chk_notif_nuevos)
        
        grupo.setLayout(layout)
        return grupo
    
    def crear_grupo_facturas(self):
        """Crea el grupo de configuración de facturas"""
        grupo = QGroupBox("🧾 Configuración de Facturas")
        grupo.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #000000;
                background-color: white;
                border: 2px solid #000000;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)
        
        layout = QFormLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 25, 20, 20)
        
        # Formato de folio
        self.txt_formato_folio = QLineEdit()
        self.txt_formato_folio.setPlaceholderText("Ej: FAC-{YYYY}-{NNNN}")
        self.aplicar_estilo_input(self.txt_formato_folio)
        
        # Auto-generar facturas
        self.chk_auto_factura = QCheckBox("Generar factura automáticamente al recibir pago")
        self.chk_auto_factura.setChecked(True)
        self.aplicar_estilo_checkbox(self.chk_auto_factura)
        
        layout.addRow("Formato de folio:", self.txt_formato_folio)
        layout.addRow("", self.chk_auto_factura)
        
        grupo.setLayout(layout)
        return grupo
    
    def aplicar_estilo_input(self, widget):
        """Aplica estilo a los inputs"""
        widget.setStyleSheet("""
            QLineEdit, QSpinBox, QComboBox {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                background-color: white;
                color: #000000;
                font-size: 13px;
            }
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
                border: 2px solid #3498db;
            }
            /* Forzar color de los items en los desplegables */
            QComboBox QAbstractItemView {
                background-color: white;
                color: #000000;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QComboBox QAbstractItemView::item {
                color: #000000;
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
            QCalendarWidget QTableView {
                color: black;
            }
            QPushButton {
                color: black;
            }
        """)
    
    def aplicar_estilo_checkbox(self, checkbox):
        """Aplica estilo a los checkboxes"""
        checkbox.setStyleSheet("""
            QCheckBox {
                color: #000000;
                font-size: 13px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border-color: #3498db;
            }
        """)
    
    def actualizar_preview_logo(self):
        """Actualiza el preview del logo"""
        if os.path.exists(self.logo_path):
            pixmap = QPixmap(self.logo_path)
            scaled_pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_preview.setPixmap(scaled_pixmap)
        else:
            self.logo_preview.setText("Sin logo\n📷")
            self.logo_preview.setStyleSheet("""
                border: 2px dashed #bdc3c7;
                background-color: #ecf0f1;
                color: #95a5a6;
                font-size: 12px;
                border-radius: 8px;
            """)
    
    def seleccionar_logo(self):
        """Permite seleccionar un nuevo logo"""
        archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Logo",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp *.ico)"
        )
        
        if archivo:
            try:
                # Copiar el archivo a la carpeta assets
                import shutil
                destino = self.logo_path
                shutil.copy2(archivo, destino)
                
                self.actualizar_preview_logo()
                # Mensaje con estilo
                msg = QMessageBox(self)
                msg.setWindowTitle("Éxito")
                msg.setText("Logo actualizado correctamente.\nReinicie la aplicación para ver los cambios.")
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
                msg.setText(f"Error al copiar el logo:\n{str(e)}")
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
    
    def eliminar_logo(self):
        """Elimina el logo actual"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Confirmar")
        msg.setText("¿Está seguro de eliminar el logo?")
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
                if os.path.exists(self.logo_path):
                    os.remove(self.logo_path)
                    self.actualizar_preview_logo()
                    # Mensaje con estilo
                    msg = QMessageBox(self)
                    msg.setWindowTitle("Éxito")
                    msg.setText("Logo eliminado correctamente.")
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
                msg.setText(f"Error al eliminar el logo:\n{str(e)}")
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
    
    def cargar_configuracion(self):
        """Carga la configuración desde el archivo JSON"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                    # Información del gimnasio
                    self.txt_nombre_gym.setText(config.get('nombre_gimnasio', 'KyoGym'))
                    self.txt_direccion.setText(config.get('direccion', ''))
                    self.txt_telefono.setText(config.get('telefono', ''))
                    self.txt_email.setText(config.get('email', ''))
                    self.txt_rfc.setText(config.get('rfc', ''))
                    
                    # Notificaciones
                    self.chk_notif_vencimiento.setChecked(config.get('notif_vencimiento', True))
                    self.chk_notif_pagos.setChecked(config.get('notif_pagos', True))
                    self.chk_notif_nuevos.setChecked(config.get('notif_nuevos', True))
                    
                    # Facturas
                    self.txt_formato_folio.setText(config.get('formato_folio', 'FAC-{YYYY}-{NNNN}'))
                    self.chk_auto_factura.setChecked(config.get('auto_factura', True))
        except Exception as e:
            msg = QMessageBox(self)
            msg.setWindowTitle("Advertencia")
            msg.setText(f"Error al cargar configuración:\n{str(e)}\n\nSe usarán valores por defecto.")
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
                    background-color: #f39c12;
                    color: white;
                    padding: 8px 20px;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 13px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #e67e22;
                }
            """)
            msg.exec()
    
    def guardar_configuracion(self):
        """Guarda la configuración en el archivo JSON"""
        try:
            dias_alerta = DEFAULT_DIAS_ALERTA_VENCIMIENTO
            if os.path.exists(self.config_file):
                try:
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        config_existente = json.load(f)
                        dias_alerta = int(config_existente.get('dias_alerta_vencimiento', DEFAULT_DIAS_ALERTA_VENCIMIENTO))
                        if dias_alerta < 0:
                            dias_alerta = DEFAULT_DIAS_ALERTA_VENCIMIENTO
                except (ValueError, TypeError, json.JSONDecodeError):
                    dias_alerta = DEFAULT_DIAS_ALERTA_VENCIMIENTO

            config = {
                'nombre_gimnasio': self.txt_nombre_gym.text(),
                'direccion': self.txt_direccion.text(),
                'telefono': self.txt_telefono.text(),
                'email': self.txt_email.text(),
                'rfc': self.txt_rfc.text(),
                'notif_vencimiento': self.chk_notif_vencimiento.isChecked(),
                'notif_pagos': self.chk_notif_pagos.isChecked(),
                'notif_nuevos': self.chk_notif_nuevos.isChecked(),
                'formato_folio': self.txt_formato_folio.text(),
                'auto_factura': self.chk_auto_factura.isChecked(),
                'dias_alerta_vencimiento': dias_alerta
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            # Mensaje con estilo
            msg = QMessageBox(self)
            msg.setWindowTitle("Éxito")
            msg.setText("Configuración guardada correctamente.")
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
            msg.setText(f"Error al guardar configuración:\n{str(e)}")
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
    
    def restaurar_predeterminados(self):
        """Restaura los valores predeterminados"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Confirmar")
        msg.setText("¿Está seguro de restaurar los valores predeterminados?")
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
            self.txt_nombre_gym.setText("KyoGym")
            self.txt_direccion.setText("")
            self.txt_telefono.setText("")
            self.txt_email.setText("")
            # Restablecer demás campos
            self.txt_rfc.setText("")
            self.chk_notif_vencimiento.setChecked(True)
            self.chk_notif_pagos.setChecked(True)
            self.chk_notif_nuevos.setChecked(True)
            self.txt_formato_folio.setText("FAC-{YYYY}-{NNNN}")
            self.chk_auto_factura.setChecked(True)
            
    def cerrar_sesion(self):
        """Cierra la sesión actual y regresa al login."""
        msg = QMessageBox(self)
        msg.setWindowTitle("Confirmar")
        msg.setText("¿Desea cerrar la sesión actual?")
        msg.setStyleSheet("""
            QMessageBox { background-color: white; }
            QLabel { color: black; font-size: 14px; min-width: 280px; border: none; }
            QPushButton {
                background-color: #2c3e50;
                color: white;
                padding: 8px 20px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 13px;
                min-width: 80px;
            }
            QPushButton:hover { background-color: #3d5166; }
        """)
        btn_si = msg.addButton("Sí", QMessageBox.YesRole)
        msg.addButton("No", QMessageBox.NoRole)
        msg.exec()
        if msg.clickedButton() != btn_si:
            return

        # Emitir señal para que MainWindow gestione el regreso al login
        self.logout_solicitado.emit()
