"""Constantes de la aplicación"""
import os
from pathlib import Path

# Nombre de la aplicación
APP_NAME = "Kyo-Gym"

# Ruta de datos de aplicación - CAMBIO: usar carpeta del proyecto
APP_DATA_DIR = Path(__file__).parent.parent  # Carpeta raíz del proyecto (c:\KyoGym)
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Ruta de la base de datos - estará en c:\KyoGym\gimnasio.db
DB_PATH = APP_DATA_DIR / "gimnasio.db"

# Estados de membresía
ESTADO_ACTIVA = "Activa"
ESTADO_POR_VENCER = "Por Vencer"
ESTADO_VENCIDA = "Vencida"

# Días para considerar "por vencer"
DIAS_ALERTA_VENCIMIENTO = 7
