# 📤 Sincronización con OneDrive - Guía Completa

Este documento explica cómo configurar y usar el script de sincronización para subir automáticamente los datos de la base de datos `gimnasio.db` a un archivo Excel en OneDrive.

---

## 📋 Requisitos Previos

1. **Cuenta de Microsoft 365** o cuenta personal de Microsoft con OneDrive
2. **Acceso al Azure Portal** para crear una aplicación
3. **Python 3.7+** instalado
4. **Dependencias Python**:
   ```bash
   pip install msal openpyxl requests
   ```

---

## 🔧 Configuración de Azure AD (Paso a Paso)

### 1. Crear una Aplicación en Azure AD

1. Ve a [Azure Portal](https://portal.azure.com)
2. Inicia sesión con tu cuenta de Microsoft
3. Busca **"Azure Active Directory"** o **"Microsoft Entra ID"**
4. En el menú lateral, selecciona **"App registrations"** (Registros de aplicaciones)
5. Haz clic en **"+ New registration"** (Nuevo registro)

### 2. Configurar la Aplicación

Completa los siguientes campos:

- **Name** (Nombre): `KyoGym OneDrive Sync` (o el nombre que prefieras)
- **Supported account types** (Tipos de cuenta compatibles):
  - Selecciona: **"Accounts in this organizational directory only"** (solo si tienes Microsoft 365)
  - O selecciona: **"Accounts in any organizational directory and personal Microsoft accounts"** (para cuentas personales)
- **Redirect URI**: Déjalo en blanco por ahora

Haz clic en **"Register"** (Registrar)

### 3. Obtener el Client ID y Tenant ID

Después de registrar la aplicación:

1. Verás la página **"Overview"** (Información general)
2. Copia los siguientes valores:
   - **Application (client) ID** → Este es tu `client_id`
   - **Directory (tenant) ID** → Este es tu `tenant_id`

### 4. Crear un Client Secret

1. En el menú lateral de tu aplicación, selecciona **"Certificates & secrets"** (Certificados y secretos)
2. Haz clic en **"+ New client secret"** (Nuevo secreto de cliente)
3. Agrega una descripción: `OneDrive Sync Secret`
4. Selecciona una expiración: **24 months** (24 meses) o la que prefieras
5. Haz clic en **"Add"** (Agregar)
6. **¡IMPORTANTE!** Copia el **Value** (Valor) inmediatamente → Este es tu `client_secret`
   - ⚠️ **Solo se muestra una vez, no podrás verlo de nuevo**

### 5. Configurar Permisos de API

1. En el menú lateral, selecciona **"API permissions"** (Permisos de API)
2. Haz clic en **"+ Add a permission"** (Agregar un permiso)
3. Selecciona **"Microsoft Graph"**
4. Selecciona **"Application permissions"** (Permisos de aplicación)
5. Busca y agrega los siguientes permisos:
   - `Files.ReadWrite.All` - Para leer y escribir archivos en OneDrive
6. Haz clic en **"Add permissions"** (Agregar permisos)
7. **¡IMPORTANTE!** Haz clic en **"Grant admin consent for [tu organización]"** (Conceder consentimiento de administrador)
   - Confirma haciendo clic en **"Yes"**

---

## ⚙️ Configuración del Script

### 1. Editar el archivo `onedrive_config.json`

Abre el archivo `onedrive_config.json` y reemplaza los valores:

```json
{
    "client_id": "AQUI_TU_CLIENT_ID",
    "client_secret": "AQUI_TU_CLIENT_SECRET",
    "tenant_id": "AQUI_TU_TENANT_ID",
    "authority": "https://login.microsoftonline.com/AQUI_TU_TENANT_ID",
    "scope": [
        "https://graph.microsoft.com/.default"
    ],
    "onedrive_folder": "/",
    "excel_filename": "gimnasio.xlsx"
}
```

### 2. Configuración Opcional

- **`onedrive_folder`**: Carpeta en OneDrive donde se guardará el archivo
  - `"/"` - Raíz de OneDrive (por defecto)
  - `"/Documentos"` - Carpeta Documentos
  - `"/KyoGym/Respaldos"` - Subcarpeta personalizada

- **`excel_filename`**: Nombre del archivo Excel
  - Por defecto: `"gimnasio.xlsx"`
  - Puedes cambiarlo a: `"respaldo_gimnasio.xlsx"`, etc.

---

## 🚀 Uso del Script

### Ejecución Manual

Ejecuta el script desde la terminal:

```bash
python sync_onedrive.py
```

### Ejecución Programada

#### Windows (Task Scheduler)

1. Abre **"Programador de tareas"** (Task Scheduler)
2. Crea una tarea básica:
   - **Nombre**: Sincronizar KyoGym con OneDrive
   - **Desencadenador**: Diariamente a las 23:00 (o cuando prefieras)
   - **Acción**: Iniciar un programa
     - **Programa**: `python` (o ruta completa: `C:\Python311\python.exe`)
     - **Argumentos**: `sync_onedrive.py`
     - **Iniciar en**: `C:\Users\David\Downloads\KyoGym\KyoGym`

#### Linux/macOS (Cron)

Edita el crontab:

```bash
crontab -e
```

Agrega la siguiente línea (sincronización diaria a las 23:00):

```bash
0 23 * * * cd /ruta/a/KyoGym && /usr/bin/python3 sync_onedrive.py
```

---

## 📊 Estructura del Archivo Excel Resultante

El archivo Excel generado contiene 3 hojas:

### 1. **Clientes**
- `id`: ID del cliente
- `nombre`: Nombre completo
- `telefono`: Teléfono de contacto
- `sexo`: Sexo del cliente
- `fecha_nacimiento`: Fecha de nacimiento
- `fecha_registro`: Fecha de registro en el gimnasio
- `activo`: Estado (1 = Activo, 0 = Inactivo)

### 2. **Membresías**
- `id`: ID de la membresía
- `cliente_id`: ID del cliente asociado
- `cliente_nombre`: Nombre del cliente
- `tipo`: Tipo de membresía
- `fecha_inicio`: Fecha de inicio
- `fecha_vencimiento`: Fecha de vencimiento
- `monto`: Monto pagado
- `pago_id`: ID del pago asociado

### 3. **Pagos**
- `id`: ID del pago
- `cliente_id`: ID del cliente
- `cliente_nombre`: Nombre del cliente
- `fecha`: Fecha del pago
- `monto`: Monto pagado
- `metodo`: Método de pago
- `concepto`: Concepto del pago

---

## 🔍 Verificación

Después de ejecutar el script:

1. Ve a [OneDrive](https://onedrive.live.com)
2. Busca el archivo `gimnasio.xlsx` en la ubicación configurada
3. Abre el archivo y verifica que contenga las 3 hojas con los datos

---

## ⚠️ Solución de Problemas

### Error: "client_id no válido"
- Verifica que hayas copiado correctamente el **Application (client) ID** de Azure Portal
- Asegúrate de que no haya espacios extra al principio o final

### Error: "client_secret no válido"
- El secreto puede haber expirado
- Crea un nuevo secreto en Azure Portal y actualiza `onedrive_config.json`

### Error: "Insufficient privileges"
- Verifica que hayas agregado el permiso `Files.ReadWrite.All`
- Asegúrate de haber hecho clic en **"Grant admin consent"**

### Error: "Base de datos no encontrada"
- Verifica que el archivo `gimnasio.db` exista en la ruta correcta
- Por defecto está en: `C:\Users\David\Downloads\KyoGym\KyoGym\gimnasio.db`

### Error de conexión
- Verifica tu conexión a internet
- Comprueba que no haya un firewall bloqueando las conexiones

---

## 🔒 Seguridad

⚠️ **IMPORTANTE**: Mantén seguro el archivo `onedrive_config.json`

- **NO** lo compartas con nadie
- **NO** lo subas a repositorios públicos (Git/GitHub)
- Considera agregar `onedrive_config.json` a tu `.gitignore`
- Los secretos expiran, renuévalos periódicamente

---

## 📝 Notas Adicionales

- El script crea un archivo Excel temporal durante la sincronización que se elimina automáticamente
- Si el archivo ya existe en OneDrive, se sobrescribirá con la versión más reciente
- La sincronización mantiene el formato y estilos del Excel (encabezados con color azul, texto centrado, etc.)
- El proceso es seguro: no modifica la base de datos original

---

## 📞 Soporte

Para problemas o preguntas adicionales:
- Consulta la [documentación de Microsoft Graph API](https://learn.microsoft.com/en-us/graph/api/overview)
- Revisa los logs de error que genera el script
- Verifica que todas las dependencias estén instaladas correctamente

---

## 📅 Última Actualización

Fecha: 14 de febrero de 2026
Versión: 1.0
