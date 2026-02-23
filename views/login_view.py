from PySide6.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont
import os
from db import verify_user
from usuario_activo import guardar_usuario_activo


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("KyoGym - Iniciar sesión")
        self.setMinimumSize(700, 420)
        # Permitir que el diálogo se muestre como ventana principal para poder maximizar
        self.setWindowFlag(Qt.Window)
        self.init_ui()

    def init_ui(self):
        root = os.path.dirname(os.path.dirname(__file__))
        assets_path = os.path.join(root, "assets")
        logo_path = os.path.join(assets_path, "logo.png")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Left panel with logo and illustration
        left = QWidget()
        left.setStyleSheet("background-color: #000000; color: white;")
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(60, 60, 60, 60)
        left_layout.setSpacing(32)

        if os.path.exists(logo_path):
            pix = QPixmap(logo_path)
            # Center-crop the pixmap to a square (head approximation)
            w = pix.width()
            h = pix.height()
            side = min(w, h)
            x = (w - side) // 2
            y = (h - side) // 4  # bias hacia la parte superior
            try:
                head = pix.copy(x, y, side, side)
            except Exception:
                head = pix
            head = head.scaled(350, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            lbl_logo = QLabel()
            lbl_logo.setPixmap(head)
            lbl_logo.setAlignment(Qt.AlignCenter)
            left_layout.setAlignment(lbl_logo, Qt.AlignHCenter)
            left_layout.addWidget(lbl_logo)

        # Botón "Crear cuenta" en el lado izquierdo
        left_layout.addStretch()
        layout.addWidget(left, 1)

        # Right panel with form
        right = QWidget()
        right.setStyleSheet("background-color: white;")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(40, 80, 40, 40)
        right_layout.setSpacing(14)

        lbl_signin = QLabel("Iniciar sesión")
        lbl_signin.setFont(QFont("Arial", 18, QFont.Bold))
        lbl_signin.setStyleSheet("color: #2c3e50;")
        right_layout.addWidget(lbl_signin)

        # Right panel with form
        right = QWidget()
        right.setStyleSheet("background-color: white;")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(40, 80, 40, 40)
        right_layout.setSpacing(14)

        lbl_signin = QLabel("Iniciar sesión")
        lbl_signin.setFont(QFont("Arial", 18, QFont.Bold))
        lbl_signin.setStyleSheet("color: #2c3e50;")
        right_layout.addWidget(lbl_signin)

        # Márgenes horizontales para centrar los inputs
        inputs_wrapper = QHBoxLayout()
        inputs_wrapper.addStretch()
        
        # Container para los inputs
        inputs_layer = QVBoxLayout()
        inputs_layer.setContentsMargins(0, 0, 0, 0)
        inputs_layer.setSpacing(14)

        self.input_user = QLineEdit()
        self.input_user.setPlaceholderText("Usuario")
        self.input_user.setMinimumHeight(44)
        self.input_user.setStyleSheet(
            "QLineEdit { padding: 8px; font-size: 14px; color: #000000; background-color: #ffffff; border: 1px solid #ddd; border-radius: 6px;}"
            "QLineEdit::placeholder { color: #9aa0a6; }"
        )
        inputs_layer.addWidget(self.input_user)

        self.input_pass = QLineEdit()
        self.input_pass.setPlaceholderText("Contraseña")
        self.input_pass.setEchoMode(QLineEdit.Password)
        self.input_pass.setMinimumHeight(44)
        self.input_pass.setStyleSheet(
            "QLineEdit { padding: 8px; font-size: 14px; color: #000000; background-color: #ffffff; border: 1px solid #ddd; border-radius: 6px;}"
            "QLineEdit::placeholder { color: #9aa0a6; }"
        )
        inputs_layer.addWidget(self.input_pass)

        self.btn_login = QPushButton("Ingresar")
        self.btn_login.setMinimumHeight(44)
        # Botón con detalle plateado
        self.btn_login.setStyleSheet(
            "QPushButton { background-color: #C0C0C0; color: #000000; border-radius: 8px; font-weight: bold; padding: 8px 12px; }"
            "QPushButton:hover { background-color: #aeb0b0; }"
        )
        self.btn_login.clicked.connect(self.attempt_login)
        inputs_layer.addWidget(self.btn_login)

        inputs_wrapper.addLayout(inputs_layer, 2)
        inputs_wrapper.addStretch()

        right_layout.addLayout(inputs_wrapper)

        # Small helper text
        hint = QLabel("Usuario por defecto: admin / admin123")
        hint.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        right_layout.addWidget(hint)

        # Row with forgot password link
        actions_layout = QHBoxLayout()

        lbl_forgot = QLabel("¿Olvidaste tu contraseña?")
        lbl_forgot.setStyleSheet("color: #3498db; text-decoration: underline;")
        lbl_forgot.setCursor(Qt.PointingHandCursor)
        lbl_forgot.mousePressEvent = lambda event: self.forgot_password()
        actions_layout.addStretch()
        actions_layout.addWidget(lbl_forgot)

        right_layout.addLayout(actions_layout)

        right_layout.addStretch()

        layout.addWidget(right, 1)

        # Estilos generales del diálogo (bordes negros y detalles dorados)
        self.setStyleSheet("""
            QDialog { background-color: #000000; }
        """)

    def attempt_login(self):
        username = self.input_user.text().strip()
        password = self.input_pass.text()
        if not username or not password:
            QMessageBox.warning(self, "Error", "Debe ingresar usuario y contraseña.")
            return

        try:
            if verify_user(username, password):
                guardar_usuario_activo(username)
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Usuario o contraseña incorrectos.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al verificar credenciales: {e}")

    def forgot_password(self):
        QMessageBox.information(self, "Recuperar contraseña", "Contacta al administrador para restablecer tu contraseña.")



