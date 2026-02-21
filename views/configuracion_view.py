"""Vista de configuración del sistema"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QFrame, QLineEdit, QPushButton, QGroupBox,
                               QFormLayout, QComboBox, QSpinBox, QCheckBox,
                               QMessageBox, QScrollArea, QFileDialog)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from utils.validators import crear_validador_nombre, TelefonoFormateadoLineEdit, crear_validador_email
import json
import os


DEFAULT_DIAS_ALERTA_VENCIMIENTO = 7


class ConfiguracionView(QWidget):
    """Vista de configuración del sistema"""
    def __init__(self):
        super().__init__()
        self.config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
        self.logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")
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
                border: 2px solid #e0e0e0;
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
            self.txt_rfc.setText("")
            self.chk_notif_vencimiento.setChecked(True)
            self.chk_notif_pagos.setChecked(True)
            self.chk_notif_nuevos.setChecked(True)
            self.txt_formato_folio.setText("FAC-{YYYY}-{NNNN}")
            self.chk_auto_factura.setChecked(True)
