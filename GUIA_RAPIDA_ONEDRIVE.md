# 🚀 Guía Rápida - Sincronización OneDrive

## 📦 Instalación Rápida

### Windows
```bash
instalar_dependencias_onedrive.bat
```

### Linux/macOS
```bash
chmod +x instalar_dependencias_onedrive.sh
./instalar_dependencias_onedrive.sh
```

### Manual
```bash
pip install msal openpyxl requests
```

---

## 🎯 ¿Qué script usar?

### 🏢 `sync_onedrive.py` - Cuentas Organizacionales (Microsoft 365)
- Requiere configurar Azure AD
- Para empresas y organizaciones
- Necesita permisos administrativos
- **Más complejo de configurar**

### 👤 `sync_onedrive_personal.py` - Cuentas Personales (RECOMENDADO)
- Autenticación interactiva simple
- Para cuentas personales de Microsoft/OneDrive
- No requiere Azure AD completo
- **Más fácil de usar** ✅

---

## 🏃 Uso Rápido (Cuenta Personal)

### 1. Ejecutar el script
```bash
python sync_onedrive_personal.py
```

### 2. Autenticarse
El script mostrará:
```
📱 AUTENTICACIÓN REQUERIDA
============================================================
To sign in, use a web browser to open the page:
https://microsoft.com/devicelogin

And enter the code: ABC-DEF-GHI
============================================================
```

### 3. Pasos en el navegador
1. Abre: https://microsoft.com/devicelogin
2. Ingresa el código mostrado (ej: ABC-DEF-GHI)
3. Inicia sesión con tu cuenta de Microsoft
4. Acepta los permisos
5. Vuelve a la terminal

### 4. ¡Listo!
El archivo `gimnasio.xlsx` se subirá automáticamente a tu OneDrive.

---

## 🏢 Uso Avanzado (Cuenta Organizacional)

### 1. Configurar Azure AD
Lee el archivo: `SYNC_ONEDRIVE_README.md` (instrucciones detalladas)

### 2. Editar configuración
Abre `onedrive_config.json` y completa:
```json
{
    "client_id": "tu-client-id-aqui",
    "client_secret": "tu-secret-aqui",
    "tenant_id": "tu-tenant-id-aqui",
    ...
}
```

### 3. Ejecutar
```bash
python sync_onedrive.py
```

---

## 📊 Resultado

El archivo Excel contendrá 4 hojas:

1. **Resumen** - Estadísticas generales y fecha
2. **Clientes** - Lista completa de clientes
3. **Membresías** - Todas las membresías registradas
4. **Pagos** - Historial de pagos

---

## ⚡ Automatización

### Windows (Tarea Programada)
1. Abre "Programador de tareas"
2. Crea tarea básica
3. Programa: Diariamente a las 23:00
4. Acción: `python` `sync_onedrive_personal.py`

### Linux/macOS (Cron)
```bash
crontab -e
```
Agrega:
```
0 23 * * * cd /ruta/KyoGym && python3 sync_onedrive_personal.py
```

---

## ⚠️ Solución Rápida de Problemas

| Problema | Solución |
|----------|----------|
| "msal no encontrado" | `pip install msal openpyxl requests` |
| "Base de datos no encontrada" | Verifica que `gimnasio.db` exista |
| "Token expirado" | Solo vuelve a ejecutar, se reautenticará automáticamente |
| "Error de conexión" | Verifica tu internet |
| Error 401/403 | Reautentícate eliminando `onedrive_token_cache.bin` |

---

## 🔒 Seguridad

### ⚠️ NUNCA SUBIR A GIT:
- `onedrive_config.json` - Credenciales
- `onedrive_config_personal.json` - Configuración
- `onedrive_token_cache.bin` - Tokens de acceso

Ya están en `.gitignore` ✅

---

## 📱 Verificación

1. Ve a: https://onedrive.live.com
2. Busca: `gimnasio.xlsx`
3. Abre y verifica las 4 hojas

---

## 💡 Consejos

- **Primera vez**: Usa `sync_onedrive_personal.py` (más simple)
- **Automatizar**: Programa para ejecutarse cada noche
- **Respaldo**: El archivo se sobrescribe, considera versionado manual
- **Internet**: Asegúrate de tener conexión estable
- **Token cache**: Se guarda localmente, no necesitas autenticarte cada vez

---

## 📞 Más Información

- Guía completa: `SYNC_ONEDRIVE_README.md`
- Configuración Azure AD: Ver sección correspondiente en el README

---

**Fecha**: Febrero 2026  
**Versión**: 1.0
