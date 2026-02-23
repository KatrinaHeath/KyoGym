"""Módulo para gestionar el usuario activo del sistema"""
from pathlib import Path
import json

# Archivo donde se guarda el usuario activo
ARCHIVO_USUARIO = Path.home() / "KyoGym" / "usuario_activo.json"


def obtener_usuario_activo():
    """Obtiene el username del usuario activo."""
    try:
        if ARCHIVO_USUARIO.exists():
            with open(ARCHIVO_USUARIO, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('usuario', 'admin')
        return 'admin'
    except Exception:
        return 'admin'


def guardar_usuario_activo(usuario):
    """Guarda el usuario activo."""
    try:
        ARCHIVO_USUARIO.parent.mkdir(parents=True, exist_ok=True)
        with open(ARCHIVO_USUARIO, 'w', encoding='utf-8') as f:
            json.dump({'usuario': usuario}, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error al guardar usuario: {e}")
        return False
