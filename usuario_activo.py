"""Módulo para gestionar el usuario activo del sistema"""
from pathlib import Path
import json

# Archivo donde se guarda el usuario activo
ARCHIVO_USUARIO = Path.home() / "KyoGym" / "usuario_activo.json"

# Usuarios disponibles
USUARIOS = ["Zahir Lay", "Brayan Bernal"]


def obtener_usuario_activo():
    """Obtiene el nombre del usuario activo"""
    try:
        if ARCHIVO_USUARIO.exists():
            with open(ARCHIVO_USUARIO, 'r', encoding='utf-8') as f:
                data = json.load(f)
                usuario = data.get('usuario', USUARIOS[0])
                # Verificar que el usuario sea válido
                if usuario in USUARIOS:
                    return usuario
        # Si no existe el archivo o el usuario no es válido, retornar el primero
        return USUARIOS[0]
    except Exception:
        return USUARIOS[0]


def guardar_usuario_activo(usuario):
    """Guarda el usuario activo"""
    try:
        # Crear directorio si no existe
        ARCHIVO_USUARIO.parent.mkdir(parents=True, exist_ok=True)
        
        # Guardar en archivo JSON
        with open(ARCHIVO_USUARIO, 'w', encoding='utf-8') as f:
            json.dump({'usuario': usuario}, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"Error al guardar usuario: {e}")
        return False
