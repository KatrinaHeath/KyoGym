"""Vista del Dashboard con métricas y próximas a vencer"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
                               QLineEdit, QPushButton)
from PySide6.QtCore import Qt, QTimer, QRect
from PySide6.QtGui import QFont, QPainter, QColor, QPen, QBrush
from services import membresia_service, pago_service, cliente_service
from utils.constants import ESTADO_ACTIVA, ESTADO_POR_VENCER, ESTADO_VENCIDA
from datetime import date
import math


class SimpleBarChart(QWidget):
    """Gráfico de barras simple"""
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(200)
        self.setMinimumWidth(300)
        self.datos = [15, 18, 22, 28, 20, 23, 25]
        self.labels = ["E", "F", "M", "A", "M", "J", "J"]
    
    def sizeHint(self):
        from PySide6.QtCore import QSize
        return QSize(500, 250)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Configuración
        width = self.width()
        height = self.height()
        margin = 40
        bar_width = (width - 2 * margin) / len(self.datos)
        max_value = max(self.datos)
        
        # Dibujar barras
        for i, value in enumerate(self.datos):
            x = margin + i * bar_width + bar_width * 0.2
            bar_height = (value / max_value) * (height - 2 * margin)
            y = height - margin - bar_height
            
            painter.fillRect(int(x), int(y), int(bar_width * 0.6), int(bar_height), QColor("#95a5a6"))
            
            # Etiqueta del mes
            painter.setPen(QColor("#666"))
            painter.drawText(int(x), height - margin + 20, int(bar_width * 0.6), 20,
                           Qt.AlignCenter, self.labels[i])


class SimplePieChart(QWidget):
    """Gráfico de torta simple"""
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(200)
        self.setMinimumWidth(200)
        self.datos = [
            ("Activa", 0, QColor("#4CAF50")),
            ("Por Vencer", 0, QColor("#FF9800")),
            ("Vencida", 0, QColor("#F44336"))
        ]
        self.setMouseTracking(True)
        self.sector_bajo_cursor = None
        self.size_increment_actual = 0.0  # Tamaño actual de agrandamiento (animado)
        self.size_increment_objetivo = 0.0  # Tamaño objetivo
        
        # Timer para animación suave
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_size)
        self.animation_timer.start(16)  # ~60 FPS
    
    def sizeHint(self):
        from PySide6.QtCore import QSize
        return QSize(300, 250)
    
    def actualizar_datos(self, activas, por_vencer, vencidas):
        """Actualiza los datos del gráfico"""
        self.datos = [
            ("Activa", activas, QColor("#4CAF50")),
            ("Por Vencer", por_vencer, QColor("#FF9800")),
            ("Vencida", vencidas, QColor("#F44336"))
        ]
        self.update()  # Repintar el widget
    
    def animate_size(self):
        """Anima suavemente el cambio de tamaño"""
        # Interpolación suave hacia el objetivo
        diferencia = self.size_increment_objetivo - self.size_increment_actual
        if abs(diferencia) > 0.1:
            self.size_increment_actual += diferencia * 0.2  # 20% de la diferencia cada frame
            self.update()
        elif abs(diferencia) > 0.01:
            self.size_increment_actual = self.size_increment_objetivo
            self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Configuración
        width = self.width()
        height = self.height()
        size = min(width, height) - 80
        x = (width - size) / 2
        y = 20
        
        # Calcular total
        total = sum(d[1] for d in self.datos)
        
        # Si no hay datos, mostrar círculo gris
        if total == 0:
            painter.setBrush(QBrush(QColor("#e0e0e0")))
            painter.setPen(QPen(Qt.white, 2))
            painter.drawEllipse(int(x), int(y), int(size), int(size))
        else:
            # Dibujar sectores normales primero
            start_angle = 90 * 16  # Empezar desde arriba (12 en punto)
            for i, (label, value, color) in enumerate(self.datos):
                if value > 0:
                    span_angle = int((value / total) * 360 * 16)
                    
                    # Dibujar todos los sectores con tamaño normal
                    if i != self.sector_bajo_cursor:
                        painter.setBrush(QBrush(color))
                        painter.setPen(QPen(Qt.white, 2))
                        painter.drawPie(int(x), int(y), int(size), int(size), start_angle, span_angle)
                    
                    start_angle += span_angle
            
            # Dibujar el sector seleccionado encima con mayor tamaño
            if self.sector_bajo_cursor is not None and self.size_increment_actual > 0.1:
                start_angle = 90 * 16
                for i, (label, value, color) in enumerate(self.datos):
                    if value > 0:
                        span_angle = int((value / total) * 360 * 16)
                        
                        if i == self.sector_bajo_cursor:
                            # Hacer el sector más grande con el tamaño actual de la animación
                            larger_size = size + self.size_increment_actual
                            larger_x = x - self.size_increment_actual / 2
                            larger_y = y - self.size_increment_actual / 2
                            
                            painter.setBrush(QBrush(color))
                            painter.setPen(QPen(Qt.white, 3))  # Borde más grueso
                            painter.drawPie(int(larger_x), int(larger_y), int(larger_size), int(larger_size), start_angle, span_angle)
                            break
                        
                        start_angle += span_angle
        
        # Leyenda con porcentajes
        legend_y = y + size + 20
        legend_x = 20
        painter.setFont(QFont("Arial", 10))
        
        for label, value, color in self.datos:
            # Cuadrado de color
            painter.fillRect(legend_x, legend_y, 15, 15, color)
            
            # Texto con porcentaje
            painter.setPen(QColor("#2c3e50"))
            porcentaje = (value / total * 100) if total > 0 else 0
            painter.drawText(legend_x + 20, legend_y + 12, f"{label}: {value}")
            
            legend_y += 20
        
        # Tooltip sobre el sector
        if self.sector_bajo_cursor is not None and total > 0:
            label, value, color = self.datos[self.sector_bajo_cursor]
            porcentaje = (value / total * 100)
            
            # Fondo del tooltip
            tooltip_text = f"{label}: {porcentaje:.1f}%"
            font = QFont("Arial", 10, QFont.Bold)
            painter.setFont(font)
            
            # Calcular tamaño del texto
            from PySide6.QtGui import QFontMetrics
            metrics = QFontMetrics(font)
            text_width = metrics.horizontalAdvance(tooltip_text)
            text_height = metrics.height()
            
            # Posición del tooltip (centro del gráfico)
            tooltip_x = int(width / 2 - text_width / 2 - 10)
            tooltip_y = int(y + size / 2 - text_height / 2 - 5)
            
            # Dibujar fondo del tooltip
            painter.setBrush(QBrush(QColor(0, 0, 0, 180)))
            painter.setPen(QPen(Qt.NoPen))
            painter.drawRoundedRect(tooltip_x, tooltip_y, text_width + 20, text_height + 10, 5, 5)
            
            # Dibujar texto del tooltip
            painter.setPen(QColor("#ffffff"))
            painter.drawText(tooltip_x + 10, tooltip_y + text_height, tooltip_text)


    def mouseMoveEvent(self, event):
        """Detecta sobre qué sector está el mouse"""
        width = self.width()
        height = self.height()
        size = min(width, height) - 80
        center_x = width / 2
        center_y = 20 + size / 2
        
        # Posición del mouse
        mouse_x = event.pos().x()
        mouse_y = event.pos().y()
        
        # Calcular distancia del centro
        dx = mouse_x - center_x
        dy = mouse_y - center_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Si está dentro del círculo
        if distance <= size / 2:
            # Calcular ángulo en grados
            # atan2 devuelve el ángulo desde el eje X positivo (3 en punto)
            # Convertimos para que 0° esté arriba (12 en punto) y vaya en sentido horario
            angle = math.atan2(dy, dx) * 180 / math.pi
            # Ajustar para que 0° esté arriba (12 en punto)
            angle = (angle - 90 + 360) % 360
            
            # Determinar en qué sector está
            total = sum(d[1] for d in self.datos)
            if total > 0:
                current_angle = 0
                for i, (label, value, color) in enumerate(self.datos):
                    if value > 0:
                        sector_angle = (value / total) * 360
                        if current_angle <= angle < current_angle + sector_angle:
                            if self.sector_bajo_cursor != i:
                                self.sector_bajo_cursor = i
                                self.size_increment_objetivo = 15.0  # Tamaño objetivo cuando hay hover
                                self.update()
                            return
                        current_angle += sector_angle
        
        # Si no está sobre ningún sector
        if self.sector_bajo_cursor is not None:
            self.sector_bajo_cursor = None
            self.size_increment_objetivo = 0.0  # Volver al tamaño normal
            self.update()
    
    def leaveEvent(self, event):
        """Limpia el tooltip cuando el mouse sale del widget"""
        if self.sector_bajo_cursor is not None:
            self.sector_bajo_cursor = None
            self.size_increment_objetivo = 0.0  # Volver al tamaño normal
            self.update()


class MetricCard(QFrame):
    """Widget de tarjeta de métrica"""
    def __init__(self, titulo, valor, color="#3498db", icono="📊"):
        super().__init__()
        self.setMinimumHeight(120)
        self.setMaximumHeight(170)
        self.setMinimumWidth(160)
        self.setStyleSheet(f"""
            MetricCard {{
                background-color: white;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(2)
        
        # Layout horizontal para icono y título
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        
        # Icono
        label_icono = QLabel(icono)
        label_icono.setStyleSheet("font-size: 24px;")
        header_layout.addWidget(label_icono)
        
        # Título
        label_titulo = QLabel(titulo)
        label_titulo.setStyleSheet("color: #666; font-size: 12px; font-weight: normal;")
        label_titulo.setAlignment(Qt.AlignLeft)
        header_layout.addWidget(label_titulo)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Valor
        label_valor = QLabel(str(valor))
        label_valor.setStyleSheet(f"color: {color}; font-size: 28px; font-weight: bold;")
        label_valor.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        label_valor.setWordWrap(True)
        
        layout.addWidget(label_valor)
        layout.addStretch()
        
        self.setLayout(layout)
        self.label_valor = label_valor
        self.color = color
    
    def actualizar_valor(self, nuevo_valor):
        """Actualiza el valor mostrado en la tarjeta"""
        self.label_valor.setText(str(nuevo_valor))


class DashboardView(QWidget):
    """Vista principal del Dashboard"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.cargar_datos()
        
        # Actualizar cada 30 segundos
        self.timer = QTimer()
        self.timer.timeout.connect(self.cargar_datos)
        self.timer.start(30000)
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header con título y búsqueda
        header_layout = QHBoxLayout()
        
        titulo = QLabel("Dashboard")
        titulo.setFont(QFont("Arial", 24, QFont.Bold))
        titulo.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(titulo)
        
        header_layout.addStretch()
        
        # Búsqueda
        self.busqueda = QLineEdit()
        self.busqueda.setPlaceholderText("Buscar...")
        self.busqueda.setMinimumWidth(250)
        self.busqueda.setMaximumWidth(400)
        self.busqueda.setStyleSheet("""
            QLineEdit {
                padding: 8px 15px;
                border: 2px solid #e0e0e0;
                border-radius: 20px;
                font-size: 13px;
                background-color: white;
                color: black;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        header_layout.addWidget(self.busqueda)
        
        layout.addLayout(header_layout)
        
        # Contenedor de métricas
        metricas_layout = QHBoxLayout()
        metricas_layout.setSpacing(15)
        
        self.card_activas = MetricCard("Membresías Activas", "0", "#4CAF50", "✅")
        self.card_por_vencer = MetricCard("Membresías por Vencer", "0", "#FF9800", "⏰")
        self.card_vencidas = MetricCard("Membresías Vencidas", "0", "#F44336", "❌")
        self.card_pagos_mes = MetricCard("Pagos del Mes", "$0", "#2196F3", "💵")
        
        metricas_layout.addWidget(self.card_activas)
        metricas_layout.addWidget(self.card_por_vencer)
        metricas_layout.addWidget(self.card_vencidas)
        metricas_layout.addWidget(self.card_pagos_mes)
        
        layout.addLayout(metricas_layout)
        
        # Contenedor de gráficos
        graficos_layout = QHBoxLayout()
        graficos_layout.setSpacing(15)
        
        # Gráfico de barras (membresías por mes)
        frame_barras = QFrame()
        frame_barras.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
            }
        """)
        layout_barras = QVBoxLayout(frame_barras)
        layout_barras.setContentsMargins(10, 10, 10, 10)
        
        self.chart_barras = SimpleBarChart()
        layout_barras.addWidget(self.chart_barras)
        
        graficos_layout.addWidget(frame_barras, 2)
        
        # Gráfico de torta (membresías por estado)
        frame_torta_membresias = QFrame()
        frame_torta_membresias.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
            }
        """)
        layout_torta_membresias = QVBoxLayout(frame_torta_membresias)
        layout_torta_membresias.setContentsMargins(10, 10, 10, 10)
        
        # Título del gráfico
        titulo_torta_membresias = QLabel("Membresías")
        titulo_torta_membresias.setFont(QFont("Arial", 14, QFont.Bold))
        titulo_torta_membresias.setStyleSheet("color: #2c3e50; padding: 5px;")
        layout_torta_membresias.addWidget(titulo_torta_membresias)
        
        self.chart_torta = SimplePieChart()
        layout_torta_membresias.addWidget(self.chart_torta)
        
        graficos_layout.addWidget(frame_torta_membresias, 1)
        
        # Gráfico de torta (clientes por sexo)
        frame_torta_sexo = QFrame()
        frame_torta_sexo.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
            }
        """)
        layout_torta_sexo = QVBoxLayout(frame_torta_sexo)
        layout_torta_sexo.setContentsMargins(10, 10, 10, 10)
        
        # Título del gráfico
        titulo_torta_sexo = QLabel("Clientes por Sexo")
        titulo_torta_sexo.setFont(QFont("Arial", 14, QFont.Bold))
        titulo_torta_sexo.setStyleSheet("color: #2c3e50; padding: 5px;")
        layout_torta_sexo.addWidget(titulo_torta_sexo)
        
        self.chart_torta_sexo = SimplePieChart()
        layout_torta_sexo.addWidget(self.chart_torta_sexo)
        
        graficos_layout.addWidget(frame_torta_sexo, 1)
        
        layout.addLayout(graficos_layout)
        
        # Contenedor de tablas
        tablas_layout = QHBoxLayout()
        tablas_layout.setSpacing(15)
        
        # Tabla de membresías
        frame_membresias = QFrame()
        frame_membresias.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
            }
        """)
        layout_membresias = QVBoxLayout(frame_membresias)
        layout_membresias.setContentsMargins(15, 15, 15, 15)
        
        label_membresias = QLabel("Membresías")
        label_membresias.setFont(QFont("Arial", 14, QFont.Bold))
        label_membresias.setStyleSheet("color: #2c3e50;")
        layout_membresias.addWidget(label_membresias)
        
        # Filtros de membresías
        filtros_layout = QHBoxLayout()
        label_filtro = QLabel("Filtro:")
        label_filtro.setStyleSheet("color: #000000; font-size: 12px;")
        filtros_layout.addWidget(label_filtro)
        
        # Estilos para botones de filtro
        estilo_botones = """
            QPushButton {
                background-color: #f0f0f0;
                color: #000000;
                padding: 5px 12px;
                border: 2px solid #d0d0d0;
                border-radius: 4px;
                font-size: 11px;
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
        
        self.btn_filtro_todas = QPushButton("Todas")
        self.btn_filtro_activas = QPushButton("Activas")
        self.btn_filtro_por_vencer = QPushButton("Por Vencer")
        self.btn_filtro_vencidas = QPushButton("Vencidas")
        
        self.btn_filtro_todas.setCheckable(True)
        self.btn_filtro_activas.setCheckable(True)
        self.btn_filtro_por_vencer.setCheckable(True)
        self.btn_filtro_vencidas.setCheckable(True)
        
        self.btn_filtro_todas.setChecked(True)
        
        self.btn_filtro_todas.clicked.connect(lambda: self.filtrar_membresias(None, self.btn_filtro_todas))
        self.btn_filtro_activas.clicked.connect(lambda: self.filtrar_membresias(ESTADO_ACTIVA, self.btn_filtro_activas))
        self.btn_filtro_por_vencer.clicked.connect(lambda: self.filtrar_membresias(ESTADO_POR_VENCER, self.btn_filtro_por_vencer))
        self.btn_filtro_vencidas.clicked.connect(lambda: self.filtrar_membresias(ESTADO_VENCIDA, self.btn_filtro_vencidas))
        
        for btn in [self.btn_filtro_todas, self.btn_filtro_activas, self.btn_filtro_por_vencer, self.btn_filtro_vencidas]:
            btn.setStyleSheet(estilo_botones)
            filtros_layout.addWidget(btn)
        
        filtros_layout.addStretch()
        layout_membresias.addLayout(filtros_layout)
        
        self.tabla_membresias = QTableWidget()
        self.tabla_membresias.setColumnCount(4)
        self.tabla_membresias.setHorizontalHeaderLabels(["Cliente", "Inicio", "Vencimiento", "Estado"])
        self.tabla_membresias.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_membresias.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_membresias.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_membresias.verticalHeader().setVisible(False)
        self.tabla_membresias.setMinimumHeight(150)
        self.tabla_membresias.setStyleSheet("""
            QTableWidget {
                gridline-color: #e0e0e0;
                font-size: 12px;
                border: none;
                background-color: white;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                color: #2c3e50;
                padding: 10px;
                font-weight: bold;
                border: none;
                border-bottom: 2px solid #e0e0e0;
                font-size: 12px;
            }
        """)
        layout_membresias.addWidget(self.tabla_membresias)
        
        tablas_layout.addWidget(frame_membresias, 3)
        
        # Tabla de últimos pagos
        frame_pagos = QFrame()
        frame_pagos.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
            }
        """)
        layout_pagos = QVBoxLayout(frame_pagos)
        layout_pagos.setContentsMargins(15, 15, 15, 15)
        
        label_pagos = QLabel("Últimos Pagos")
        label_pagos.setFont(QFont("Arial", 14, QFont.Bold))
        label_pagos.setStyleSheet("color: #2c3e50;")
        layout_pagos.addWidget(label_pagos)
        
        self.tabla_pagos = QTableWidget()
        self.tabla_pagos.setColumnCount(4)
        self.tabla_pagos.setHorizontalHeaderLabels(["Cliente", "Fecha", "Monto", "Método"])
        self.tabla_pagos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_pagos.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_pagos.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_pagos.verticalHeader().setVisible(False)
        self.tabla_pagos.setMinimumHeight(150)
        self.tabla_pagos.setStyleSheet("""
            QTableWidget {
                gridline-color: #e0e0e0;
                font-size: 12px;
                border: none;
                background-color: white;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                color: #2c3e50;
                padding: 10px;
                font-weight: bold;
                border: none;
                border-bottom: 2px solid #e0e0e0;
                font-size: 12px;
            }
        """)
        layout_pagos.addWidget(self.tabla_pagos)
        
        tablas_layout.addWidget(frame_pagos, 2)
        
        layout.addLayout(tablas_layout)
        
        self.setLayout(layout)
    
    def cargar_datos(self):
        """Carga los datos del dashboard"""
        # Obtener conteo de membresías
        conteo = membresia_service.contar_membresias_por_estado()
        
        self.card_activas.actualizar_valor(conteo[ESTADO_ACTIVA])
        self.card_por_vencer.actualizar_valor(conteo[ESTADO_POR_VENCER])
        self.card_vencidas.actualizar_valor(conteo[ESTADO_VENCIDA])
        
        # Actualizar gráfico de torta con datos reales
        self.chart_torta.actualizar_datos(
            conteo[ESTADO_ACTIVA],
            conteo[ESTADO_POR_VENCER],
            conteo[ESTADO_VENCIDA]
        )
        
        # Actualizar gráfico de sexo
        conteo_sexo = cliente_service.contar_clientes_por_sexo()
        self.chart_torta_sexo.datos = [
            ("Masculino", conteo_sexo['Masculino'], QColor("#2196F3")),
            ("Femenino", conteo_sexo['Femenino'], QColor("#E91E63")),
            ("Otro", conteo_sexo['Otro'], QColor("#9C27B0"))
        ]
        self.chart_torta_sexo.update()
        
        # Obtener total de pagos del mes
        total_mes = pago_service.calcular_total_mes()
        self.card_pagos_mes.actualizar_valor(f"${total_mes:,.2f}")
        
        # Cargar tablas
        self.cargar_tabla_membresias()
        self.cargar_tabla_pagos()
    
    def filtrar_membresias(self, estado, boton_activo):
        """Filtra las membresías por estado"""
        # Desmarcar todos los botones
        self.btn_filtro_todas.setChecked(False)
        self.btn_filtro_activas.setChecked(False)
        self.btn_filtro_por_vencer.setChecked(False)
        self.btn_filtro_vencidas.setChecked(False)
        
        # Marcar el botón activo
        boton_activo.setChecked(True)
        
        # Cargar tabla con filtro
        self.cargar_tabla_membresias(estado)
    
    def cargar_tabla_membresias(self, filtro_estado=None):
        """Carga la tabla de membresías recientes"""
        if filtro_estado:
            membresias = [m for m in membresia_service.listar_membresias() if m['estado'] == filtro_estado][:5]
        else:
            membresias = membresia_service.listar_membresias()[:5]
        
        self.tabla_membresias.setRowCount(len(membresias))
        
        for i, membresia in enumerate(membresias):
            # Cliente - color negro
            cliente_item = QTableWidgetItem(membresia['cliente_nombre'])
            cliente_item.setForeground(QColor("#000000"))
            self.tabla_membresias.setItem(i, 0, cliente_item)
            
            # Inicio - color negro
            inicio_item = QTableWidgetItem(membresia['fecha_inicio'])
            inicio_item.setForeground(QColor("#000000"))
            self.tabla_membresias.setItem(i, 1, inicio_item)
            
            # Vencimiento - color negro
            vencimiento_item = QTableWidgetItem(membresia['fecha_vencimiento'])
            vencimiento_item.setForeground(QColor("#000000"))
            self.tabla_membresias.setItem(i, 2, vencimiento_item)
            
            # Estado con color
            estado = membresia['estado']
            estado_item = QTableWidgetItem(estado)
            
            if estado == ESTADO_ACTIVA:
                estado_item.setForeground(QColor("#4CAF50"))
            elif estado == ESTADO_POR_VENCER:
                estado_item.setForeground(QColor("#FF9800"))
            elif estado == ESTADO_VENCIDA:
                estado_item.setForeground(QColor("#F44336"))
            
            self.tabla_membresias.setItem(i, 3, estado_item)
    
    def cargar_tabla_pagos(self):
        """Carga la tabla de últimos pagos"""
        pagos = pago_service.obtener_ultimos_pagos(limite=5)
        
        self.tabla_pagos.setRowCount(len(pagos))
        
        for i, pago in enumerate(pagos):
            # Cliente - color negro
            cliente_item = QTableWidgetItem(pago['cliente_nombre'])
            cliente_item.setForeground(QColor("#000000"))
            self.tabla_pagos.setItem(i, 0, cliente_item)
            
            # Fecha - color negro
            fecha_item = QTableWidgetItem(pago['fecha'])
            fecha_item.setForeground(QColor("#000000"))
            self.tabla_pagos.setItem(i, 1, fecha_item)
            
            # Monto - color negro
            monto_item = QTableWidgetItem(f"${pago['monto']:,.2f}")
            monto_item.setForeground(QColor("#000000"))
            self.tabla_pagos.setItem(i, 2, monto_item)
            
            # Método - color negro
            metodo_item = QTableWidgetItem(pago['metodo'])
            metodo_item.setForeground(QColor("#000000"))
            self.tabla_pagos.setItem(i, 3, metodo_item)
