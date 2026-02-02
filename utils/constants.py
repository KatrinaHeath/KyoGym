"""Constantes de la aplicación"""
import os
from pathlib import Path

# Nombre de la aplicación
APP_NAME = "GymApp"

# Ruta de datos de aplicación
APP_DATA_DIR = Path(os.getenv('APPDATA')) / APP_NAME
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Ruta de la base de datos
DB_PATH = APP_DATA_DIR / "gimnasio.db"

# Estados de membresía
ESTADO_ACTIVA = "Activa"
ESTADO_POR_VENCER = "Por Vencer"
ESTADO_VENCIDA = "Vencida"

# Días para considerar "por vencer"
DIAS_ALERTA_VENCIMIENTO = 7
