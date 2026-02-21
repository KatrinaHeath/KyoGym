"""Validadores para campos de entrada en PySide6"""
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression
from PySide6.QtWidgets import QLineEdit


def crear_validador_numerico_decimal():
    """Crea un validador para campos numéricos con decimales (puntos)
    Solo acepta números y un punto decimal
    Ejemplos: 10, 10.5, 0.99"""
    regex = QRegularExpression(r"^\d*\.?\d*$")
    return QRegularExpressionValidator(regex)


def crear_validador_entero():
    """Crea un validador para campos de números enteros
    Solo acepta números sin decimales
    Ejemplos: 10, 5, 100"""
    regex = QRegularExpression(r"^\d*$")
    return QRegularExpressionValidator(regex)


def crear_validador_nombre():
    """Crea un validador para campos de nombre
    Solo acepta letras, espacios, guiones y apóstrofos
    Ejemplos: Juan, María García, José-Luis"""
    # Permite letras (mayúsculas y minúsculas), espacios, guiones y apóstrofos
    # También permite caracteres acentuados
    regex = QRegularExpression(r"^[a-zA-ZáéíóúñÁÉÍÓÚÑ\s\-']*$")
    return QRegularExpressionValidator(regex)


def crear_validador_telefono():
    """Crea un validador para campos de teléfono (formato general)
    Solo acepta números, espacios, guiones, paréntesis y el signo +
    Ejemplos: +50767686213, (555) 123-4567, 555 123 4567"""
    regex = QRegularExpression(r"^[0-9\s\-\(\)\+]*$")
    return QRegularExpressionValidator(regex)


class TelefonoFormateadoLineEdit(QLineEdit):
    """QLineEdit personalizado para teléfono con formato XXXX-XXXX
    Inserta el guion automáticamente después del 4to dígito
    y lo elimina si se borra
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("1234-5678")
        # Conectar el evento de cambio de texto
        self.textChanged.connect(self._formatear_telefono)
        # Validador para solo permitir números
        regex = QRegularExpression(r"^\d*$")
        self.setValidator(QRegularExpressionValidator(regex))
    
    def _formatear_telefono(self):
        """Formatea el teléfono automáticamente con guion después del 4to dígito
        Solo permite números, rechaza cualquier letra o carácter especial
        """
        # Remover TODOS los caracteres que no sean dígitos
        texto = ''.join(c for c in self.text() if c.isdigit())
        
        # Limitar a 8 dígitos máximo
        if len(texto) > 8:
            texto = texto[:8]
        
        # Insertar guion después del 4to dígito
        if len(texto) > 4:
            texto_formateado = texto[:4] + "-" + texto[4:]
        else:
            texto_formateado = texto
        
        # Actualizar el campo sin disparar el evento nuevamente
        if self.text() != texto_formateado:
            cursor_pos = self.cursorPosition()
            self.blockSignals(True)
            self.setText(texto_formateado)
            self.blockSignals(False)
            
            # Mantener la posición del cursor de forma inteligente
            if cursor_pos <= 4:
                self.setCursorPosition(cursor_pos)
            else:
                self.setCursorPosition(min(cursor_pos + 1, len(texto_formateado)))


def crear_validador_email():
    """Crea un validador para campos de email
    Acepta caracteres válidos para email"""
    regex = QRegularExpression(r"^[a-zA-Z0-9._\-@]*$")
    return QRegularExpressionValidator(regex)
