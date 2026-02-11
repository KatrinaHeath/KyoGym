"""Módulo para generar facturas en PDF"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime, date, timedelta
import os
from pathlib import Path
import sys

# Importar función para obtener usuario activo
sys.path.insert(0, str(Path(__file__).parent.parent))
from usuario_activo import obtener_usuario_activo


def generar_factura_membresia(membresia, cliente, ruta_salida=None):
    """
    Genera una factura PDF para una membresía
    
    Args:
        membresia: Diccionario con datos de la membresía (id, tipo, fecha_inicio, fecha_vencimiento, monto)
        cliente: Diccionario con datos del cliente (nombre, telefono)
        ruta_salida: Ruta donde guardar el PDF (opcional)
    
    Returns:
        Ruta del archivo PDF generado
    """
    # Definir ruta de salida
    if ruta_salida is None:
        carpeta_facturas = Path.home() / "KyoGym" / "Facturas"
        carpeta_facturas.mkdir(parents=True, exist_ok=True)
        ruta_salida = carpeta_facturas / f"Factura_{membresia['id']}.pdf"
    
    # Crear el documento PDF con tamaño de ticket (80mm de ancho)
    ancho_ticket = 80 * mm
    alto_ticket = 200 * mm
    
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(str(ruta_salida), pagesize=(ancho_ticket, alto_ticket))
    
    # Configurar fuentes
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    
    # Usar fuente por defecto
    fuente_normal = "Helvetica"
    fuente_bold = "Helvetica-Bold"
    
    # Posición inicial
    y_pos = alto_ticket - 10 * mm
    margen_izq = 5 * mm
    ancho_contenido = ancho_ticket - 2 * margen_izq
    
    # Logo circular (si existe)
    # Buscar logo2 en assets
    logo_path = Path(__file__).parent.parent / "assets" / "logo2.png"
    if logo_path.exists():
        # Crear un logo circular
        from PIL import Image, ImageDraw
        img_size = 200
        # Abrir imagen
        img = Image.open(str(logo_path)).convert('RGBA')
        img = img.resize((img_size, img_size), Image.Resampling.LANCZOS)
        # Crear máscara circular
        mask = Image.new('L', (img_size, img_size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse([0, 0, img_size, img_size], fill=255)
        # Aplicar máscara
        img.putalpha(mask)
        # Guardar temporalmente
        temp_logo = Path(__file__).parent.parent / ".temp_logo_circular.png"
        img.save(str(temp_logo))
        # Dibujar en PDF
        img_width = 20 * mm
        img_height = 20 * mm
        x_logo = (ancho_ticket - img_width) / 2
        c.drawImage(str(temp_logo), x_logo, y_pos - img_height, width=img_width, height=img_height, mask='auto')
        y_pos -= img_height + 5 * mm
        # Limpiar temporal
        try:
            temp_logo.unlink()
        except:
            pass
    
    # Título "Kyo-Gym"
    c.setFont(fuente_bold, 16)
    texto = "Kyo-Gym"
    ancho_texto = c.stringWidth(texto, fuente_bold, 16)
    x_centrado = (ancho_ticket - ancho_texto) / 2
    c.drawString(x_centrado, y_pos, texto)
    y_pos -= 6 * mm
    
    # Número de factura (ID de membresía)
    c.setFont(fuente_bold, 14)
    numero_factura = f"#{membresia['id']}"
    ancho_texto = c.stringWidth(numero_factura, fuente_bold, 14)
    x_centrado = (ancho_ticket - ancho_texto) / 2
    c.drawString(x_centrado, y_pos, numero_factura)
    y_pos -= 6 * mm
    
    # Información del gimnasio
    c.setFont(fuente_normal, 8)
    info_gym = "63858851"
    ancho_texto = c.stringWidth(info_gym, fuente_normal, 8)
    x_centrado = (ancho_ticket - ancho_texto) / 2
    c.drawString(x_centrado, y_pos, info_gym)
    y_pos -= 4 * mm
    
    # Atendió
    c.setFont(fuente_normal, 8)
    usuario_actual = obtener_usuario_activo()
    atendio = f"Atendió: {usuario_actual}"
    ancho_texto = c.stringWidth(atendio, fuente_normal, 8)
    x_centrado = (ancho_ticket - ancho_texto) / 2
    c.drawString(x_centrado, y_pos, atendio)
    y_pos -= 6 * mm
    
    # Nombre del cliente
    c.setFont(fuente_bold, 10)
    c.drawImage(str(Path(__file__).parent / "user_icon.png") if (Path(__file__).parent / "user_icon.png").exists() else None, 
                margen_izq, y_pos - 3*mm, width=3*mm, height=3*mm, mask='auto') if (Path(__file__).parent / "user_icon.png").exists() else None
    
    # Si no hay icono, solo mostrar el nombre
    c.setFont(fuente_bold, 10)
    c.drawString(margen_izq, y_pos, cliente['nombre'])
    y_pos -= 5 * mm
    
    # Teléfono
    c.setFont(fuente_normal, 8)
    if cliente.get('telefono'):
        c.drawString(margen_izq, y_pos, cliente['telefono'])
        y_pos -= 6 * mm
    
    # Línea separadora
    y_pos -= 2 * mm
    c.line(margen_izq, y_pos, ancho_ticket - margen_izq, y_pos)
    y_pos -= 5 * mm
    
    # Encabezado de artículos
    c.setFont(fuente_bold, 9)
    c.drawString(margen_izq, y_pos, f"1 artículos (Cant.: 1)")
    y_pos -= 6 * mm
    
    # Línea separadora
    c.line(margen_izq, y_pos, ancho_ticket - margen_izq, y_pos)
    y_pos -= 5 * mm
    
    # Artículo: Mensualidad
    c.setFont(fuente_normal, 9)
    c.drawString(margen_izq, y_pos, "1x  Mensualidad")
    monto_texto = f"${membresia['monto']:.2f}"
    ancho_monto = c.stringWidth(monto_texto, fuente_normal, 9)
    c.drawString(ancho_ticket - margen_izq - ancho_monto, y_pos, monto_texto)
    y_pos -= 6 * mm
    
    # Fechas de la mensualidad
    c.setFont(fuente_normal, 7)
    fecha_inicio = datetime.fromisoformat(membresia['fecha_inicio']).strftime("%d/%m/%Y")
    fecha_fin = datetime.fromisoformat(membresia['fecha_vencimiento']).strftime("%d/%m/%Y")
    periodo_texto = f"Válido: {fecha_inicio} - {fecha_fin}"
    ancho_texto = c.stringWidth(periodo_texto, fuente_normal, 7)
    x_centrado = (ancho_ticket - ancho_texto) / 2
    c.drawString(x_centrado, y_pos, periodo_texto)
    y_pos -= 6 * mm
    
    # Línea separadora
    c.line(margen_izq, y_pos, ancho_ticket - margen_izq, y_pos)
    y_pos -= 5 * mm
    
    # Subtotal
    c.setFont(fuente_normal, 9)
    c.drawString(ancho_ticket - margen_izq - 25*mm, y_pos, "Subtotal:")
    subtotal_texto = f"${membresia['monto']:.2f}"
    ancho_subtotal = c.stringWidth(subtotal_texto, fuente_normal, 9)
    c.drawString(ancho_ticket - margen_izq - ancho_subtotal, y_pos, subtotal_texto)
    y_pos -= 5 * mm
    
    # Total
    c.setFont(fuente_bold, 12)
    c.drawString(ancho_ticket - margen_izq - 25*mm, y_pos, "Total:")
    total_texto = f"${membresia['monto']:.2f}"
    ancho_total = c.stringWidth(total_texto, fuente_bold, 12)
    c.drawString(ancho_ticket - margen_izq - ancho_total, y_pos, total_texto)
    y_pos -= 6 * mm
    
    # Efectivo
    c.setFont(fuente_normal, 9)
    c.drawString(ancho_ticket - margen_izq - 25*mm, y_pos, "Efectivo:")
    efectivo_texto = f"${membresia['monto']:.2f}"
    ancho_efectivo = c.stringWidth(efectivo_texto, fuente_normal, 9)
    c.drawString(ancho_ticket - margen_izq - ancho_efectivo, y_pos, efectivo_texto)
    y_pos -= 5 * mm
    
    # Cambio
    c.setFont(fuente_normal, 9)
    c.drawString(ancho_ticket - margen_izq - 25*mm, y_pos, "Cambio:")
    cambio_texto = "$0.00"
    ancho_cambio = c.stringWidth(cambio_texto, fuente_normal, 9)
    c.drawString(ancho_ticket - margen_izq - ancho_cambio, y_pos, cambio_texto)
    y_pos -= 8 * mm
    
    # Línea separadora
    c.line(margen_izq, y_pos, ancho_ticket - margen_izq, y_pos)
    y_pos -= 5 * mm
    
    # Mensaje de agradecimiento
    c.setFont(fuente_bold, 10)
    mensaje = "Gracias por su compra"
    ancho_texto = c.stringWidth(mensaje, fuente_bold, 10)
    x_centrado = (ancho_ticket - ancho_texto) / 2
    c.drawString(x_centrado, y_pos, mensaje)
    y_pos -= 5 * mm
    
    # Fecha y hora
    c.setFont(fuente_normal, 8)
    fecha_hora = datetime.now().strftime("%B %d, %Y %I:%M %p")
    # Traducir mes al español
    meses = {
        'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo', 'April': 'Abril',
        'May': 'Mayo', 'June': 'Junio', 'July': 'Julio', 'August': 'Agosto',
        'September': 'Septiembre', 'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
    }
    for eng, esp in meses.items():
        fecha_hora = fecha_hora.replace(eng, esp)
    # Cambiar AM/PM a a.m./p.m.
    fecha_hora = fecha_hora.replace('AM', 'a. m.').replace('PM', 'p. m.')
    
    ancho_texto = c.stringWidth(fecha_hora, fuente_normal, 8)
    x_centrado = (ancho_ticket - ancho_texto) / 2
    c.drawString(x_centrado, y_pos, fecha_hora)
    
    # Guardar PDF
    c.save()
    
    return str(ruta_salida)


def abrir_factura(ruta_pdf):
    """Abre la factura generada con el visor de PDF del sistema"""
    import subprocess
    import platform
    
    sistema = platform.system()
    
    if sistema == "Windows":
        os.startfile(ruta_pdf)
    elif sistema == "Darwin":  # macOS
        subprocess.run(["open", ruta_pdf])
    else:  # Linux
        subprocess.run(["xdg-open", ruta_pdf])


def generar_factura_pago(pago, cliente, ruta_salida=None):
    """
    Genera una factura PDF para un pago (mismo diseño que membresía)
    
    Args:
        pago: Diccionario con datos del pago (id, fecha, monto, metodo, concepto)
        cliente: Diccionario con datos del cliente (nombre, telefono)
        ruta_salida: Ruta donde guardar el PDF (opcional)
    
    Returns:
        Ruta del archivo PDF generado
    """
    # Definir ruta de salida
    if ruta_salida is None:
        carpeta_facturas = Path.home() / "KyoGym" / "Facturas"
        carpeta_facturas.mkdir(parents=True, exist_ok=True)
        ruta_salida = carpeta_facturas / f"Factura_{pago['id']}.pdf"
    
    # Crear el documento PDF con tamaño de ticket (80mm de ancho)
    ancho_ticket = 80 * mm
    alto_ticket = 200 * mm
    
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(str(ruta_salida), pagesize=(ancho_ticket, alto_ticket))
    
    # Configurar fuentes
    fuente_normal = "Helvetica"
    fuente_bold = "Helvetica-Bold"
    
    # Posición inicial
    y_pos = alto_ticket - 10 * mm
    margen_izq = 5 * mm
    ancho_contenido = ancho_ticket - 2 * margen_izq
    
    # Logo circular (si existe)
    # Buscar logo2 en assets
    logo_path = Path(__file__).parent.parent / "assets" / "logo2.png"
    if logo_path.exists():
        # Crear un logo circular
        from PIL import Image, ImageDraw
        img_size = 200
        # Abrir imagen
        img = Image.open(str(logo_path)).convert('RGBA')
        img = img.resize((img_size, img_size), Image.Resampling.LANCZOS)
        # Crear máscara circular
        mask = Image.new('L', (img_size, img_size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse([0, 0, img_size, img_size], fill=255)
        # Aplicar máscara
        img.putalpha(mask)
        # Guardar temporalmente
        temp_logo = Path(__file__).parent.parent / ".temp_logo_circular.png"
        img.save(str(temp_logo))
        # Dibujar en PDF
        img_width = 20 * mm
        img_height = 20 * mm
        x_logo = (ancho_ticket - img_width) / 2
        c.drawImage(str(temp_logo), x_logo, y_pos - img_height, width=img_width, height=img_height, mask='auto')
        y_pos -= img_height + 5 * mm
        # Limpiar temporal
        try:
            temp_logo.unlink()
        except:
            pass
    
    # Título "Kyo-Gym"
    c.setFont(fuente_bold, 16)
    texto = "Kyo-Gym"
    ancho_texto = c.stringWidth(texto, fuente_bold, 16)
    x_centrado = (ancho_ticket - ancho_texto) / 2
    c.drawString(x_centrado, y_pos, texto)
    y_pos -= 6 * mm
    
    # Número de factura (ID de pago)
    c.setFont(fuente_bold, 14)
    numero_factura = f"#{pago['id']}"
    ancho_texto = c.stringWidth(numero_factura, fuente_bold, 14)
    x_centrado = (ancho_ticket - ancho_texto) / 2
    c.drawString(x_centrado, y_pos, numero_factura)
    y_pos -= 6 * mm
    
    # Información del gimnasio
    c.setFont(fuente_normal, 8)
    info_gym = "63858851"
    ancho_texto = c.stringWidth(info_gym, fuente_normal, 8)
    x_centrado = (ancho_ticket - ancho_texto) / 2
    c.drawString(x_centrado, y_pos, info_gym)
    y_pos -= 4 * mm
    
    # Atendió
    c.setFont(fuente_normal, 8)
    usuario_actual = obtener_usuario_activo()
    atendio = f"Atendió: {usuario_actual}"
    ancho_texto = c.stringWidth(atendio, fuente_normal, 8)
    x_centrado = (ancho_ticket - ancho_texto) / 2
    c.drawString(x_centrado, y_pos, atendio)
    y_pos -= 6 * mm
    
    # Nombre del cliente
    c.setFont(fuente_bold, 10)
    c.drawString(margen_izq, y_pos, cliente['nombre'])
    y_pos -= 5 * mm
    
    # Teléfono
    c.setFont(fuente_normal, 8)
    if cliente.get('telefono'):
        c.drawString(margen_izq, y_pos, cliente['telefono'])
        y_pos -= 6 * mm
    
    # Línea separadora
    y_pos -= 2 * mm
    c.line(margen_izq, y_pos, ancho_ticket - margen_izq, y_pos)
    y_pos -= 5 * mm
    
    # Encabezado de artículos
    c.setFont(fuente_bold, 9)
    c.drawString(margen_izq, y_pos, f"1 artículos (Cant.: 1)")
    y_pos -= 6 * mm
    
    # Línea separadora
    c.line(margen_izq, y_pos, ancho_ticket - margen_izq, y_pos)
    y_pos -= 5 * mm
    
    # Artículo: Pago
    c.setFont(fuente_normal, 9)
    concepto = pago.get('concepto', 'Pago')
    c.drawString(margen_izq, y_pos, f"1x  {concepto}")
    monto_texto = f"${pago['monto']:.2f}"
    ancho_monto = c.stringWidth(monto_texto, fuente_normal, 9)
    c.drawString(ancho_ticket - margen_izq - ancho_monto, y_pos, monto_texto)
    y_pos -= 6 * mm
    
    # Fecha del pago
    c.setFont(fuente_normal, 7)
    fecha_pago = pago.get('fecha', datetime.now().strftime('%d/%m/%Y'))
    fecha_texto = f"Cobranza: {fecha_pago}"
    ancho_texto = c.stringWidth(fecha_texto, fuente_normal, 7)
    x_centrado = (ancho_ticket - ancho_texto) / 2
    c.drawString(x_centrado, y_pos, fecha_texto)
    y_pos -= 6 * mm
    
    # Método de pago
    c.setFont(fuente_normal, 7)
    metodo = pago.get('metodo', 'Efectivo')
    metodo_texto = f"Método: {metodo}"
    ancho_texto = c.stringWidth(metodo_texto, fuente_normal, 7)
    x_centrado = (ancho_ticket - ancho_texto) / 2
    c.drawString(x_centrado, y_pos, metodo_texto)
    y_pos -= 6 * mm
    
    # Línea separadora
    c.line(margen_izq, y_pos, ancho_ticket - margen_izq, y_pos)
    y_pos -= 5 * mm
    
    # Subtotal
    c.setFont(fuente_normal, 9)
    c.drawString(ancho_ticket - margen_izq - 25*mm, y_pos, "Subtotal:")
    subtotal_texto = f"${pago['monto']:.2f}"
    ancho_subtotal = c.stringWidth(subtotal_texto, fuente_normal, 9)
    c.drawString(ancho_ticket - margen_izq - ancho_subtotal, y_pos, subtotal_texto)
    y_pos -= 5 * mm
    
    # Total
    c.setFont(fuente_bold, 12)
    c.drawString(ancho_ticket - margen_izq - 25*mm, y_pos, "Total:")
    total_texto = f"${pago['monto']:.2f}"
    ancho_total = c.stringWidth(total_texto, fuente_bold, 12)
    c.drawString(ancho_ticket - margen_izq - ancho_total, y_pos, total_texto)
    y_pos -= 6 * mm
    
    # Efectivo
    c.setFont(fuente_normal, 9)
    c.drawString(ancho_ticket - margen_izq - 25*mm, y_pos, "Efectivo:")
    efectivo_texto = f"${pago['monto']:.2f}"
    ancho_efectivo = c.stringWidth(efectivo_texto, fuente_normal, 9)
    c.drawString(ancho_ticket - margen_izq - ancho_efectivo, y_pos, efectivo_texto)
    y_pos -= 5 * mm
    
    # Cambio
    c.setFont(fuente_normal, 9)
    c.drawString(ancho_ticket - margen_izq - 25*mm, y_pos, "Cambio:")
    cambio_texto = "$0.00"
    ancho_cambio = c.stringWidth(cambio_texto, fuente_normal, 9)
    c.drawString(ancho_ticket - margen_izq - ancho_cambio, y_pos, cambio_texto)
    y_pos -= 8 * mm
    
    # Línea separadora
    c.line(margen_izq, y_pos, ancho_ticket - margen_izq, y_pos)
    y_pos -= 5 * mm
    
    # Mensaje de agradecimiento
    c.setFont(fuente_bold, 10)
    mensaje = "Gracias por su compra"
    ancho_texto = c.stringWidth(mensaje, fuente_bold, 10)
    x_centrado = (ancho_ticket - ancho_texto) / 2
    c.drawString(x_centrado, y_pos, mensaje)
    y_pos -= 5 * mm
    
    # Fecha y hora
    c.setFont(fuente_normal, 8)
    fecha_hora = datetime.now().strftime("%B %d, %Y %I:%M %p")
    # Traducir mes al español
    meses = {
        'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo', 'April': 'Abril',
        'May': 'Mayo', 'June': 'Junio', 'July': 'Julio', 'August': 'Agosto',
        'September': 'Septiembre', 'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
    }
    for eng, esp in meses.items():
        fecha_hora = fecha_hora.replace(eng, esp)
    # Cambiar AM/PM a a.m./p.m.
    fecha_hora = fecha_hora.replace('AM', 'a. m.').replace('PM', 'p. m.')
    
    ancho_texto = c.stringWidth(fecha_hora, fuente_normal, 8)
    x_centrado = (ancho_ticket - ancho_texto) / 2
    c.drawString(x_centrado, y_pos, fecha_hora)
    
    # Guardar PDF
    c.save()
    
    return str(ruta_salida)
