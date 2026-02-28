import os

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QBrush, QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QPushButton

_ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")


def _svg_icon_color(nombre_svg: str, color: QColor, size: int = 18) -> QIcon:
    """Carga un SVG desde /assets y tiñe todos los píxeles al color indicado."""
    path = os.path.join(_ASSETS, nombre_svg)
    renderer = QSvgRenderer(path)
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing)
    renderer.render(painter)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(pix.rect(), color)
    painter.end()
    return QIcon(pix)


def _svg_icon_blanco(nombre_svg: str, size: int = 18) -> QIcon:
    """Mantiene compatibilidad: devuelve ícono blanco."""
    return _svg_icon_color(nombre_svg, QColor("white"), size)


def crear_boton_icono(
    nombre_svg: str,
    bg_color: str,
    hover_color: str,
    tooltip: str,
    btn_size: int = 34,
    icon_size: int = 19,
) -> QPushButton:
    """Devuelve un QPushButton con ícono SVG negro sobre fondo transparente."""
    btn = QPushButton()
    btn.setIcon(_svg_icon_color(nombre_svg, QColor("#1a1a1a"), icon_size))
    btn.setIconSize(QSize(icon_size, icon_size))
    btn.setFixedSize(btn_size, btn_size)
    btn.setToolTip(tooltip)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setStyleSheet("""
        QPushButton {
            background-color: transparent;
            border: none;
        }
        QPushButton:hover {
            background-color: #e0e0e0;
            border-radius: 4px;
        }
        QPushButton:disabled {
            opacity: 0.4;
        }
    """)
    return btn


def crear_widget_centrado(widget) -> QPushButton:
    """Envuelve cualquier widget en un contenedor transparente y centrado."""
    from PySide6.QtWidgets import QWidget, QHBoxLayout
    container = QWidget()
    container.setStyleSheet("background: transparent; border: none;")
    lay = QHBoxLayout(container)
    lay.setContentsMargins(0, 4, 0, 4)
    lay.setAlignment(Qt.AlignCenter)
    lay.addWidget(widget)
    return container


def crear_icono_ojo(size=16, color=QColor("#1a1a1a")):
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)

    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing, True)

    pen = QPen(color)
    pen.setWidth(2)
    painter.setPen(pen)
    painter.setBrush(Qt.NoBrush)

    path = QPainterPath()
    path.moveTo(1, size / 2)
    path.quadTo(size / 2, 1, size - 1, size / 2)
    path.quadTo(size / 2, size - 1, 1, size / 2)
    painter.drawPath(path)

    painter.setPen(Qt.NoPen)
    painter.setBrush(QBrush(color))
    pupil_size = max(3, size // 4)
    pupil_x = (size - pupil_size) / 2
    pupil_y = (size - pupil_size) / 2
    painter.drawEllipse(pupil_x, pupil_y, pupil_size, pupil_size)

    painter.end()
    return QIcon(pix)
