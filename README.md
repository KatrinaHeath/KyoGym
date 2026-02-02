# KyoGym - Sistema de Gestión de Gimnasio

Aplicación de escritorio para Windows desarrollada con Python y PySide6 (Qt) para la gestión completa de un gimnasio.

## 📋 Características

- **Dashboard**: Métricas en tiempo real (membresías activas, por vencer, vencidas, pagos del mes)
- **Gestión de Membresías**: Crear, visualizar y filtrar membresías con cálculo automático de estados
- **Registro de Pagos**: Control completo de pagos con múltiples métodos
- **Base de datos SQLite**: Almacenamiento seguro en AppData/Roaming/GymApp
- **Interfaz moderna**: UI limpia y profesional con PySide6

## 🚀 Instalación y Ejecución

### Requisitos Previos
- Python 3.11 o superior
- Windows 10/11

### Paso 1: Crear Entorno Virtual

Abre **VS Code** en la carpeta del proyecto y luego abre una terminal (Terminal → New Terminal):

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate
```

### Paso 2: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 3: Ejecutar la Aplicación

```bash
python main.py
```

La aplicación se abrirá y creará automáticamente la base de datos en:
```
C:\Users\TuUsuario\AppData\Roaming\GymApp\gimnasio.db
```

## 📦 Empaquetado con PyInstaller

Para crear un ejecutable `.exe` que puedas colocar en el escritorio:

### Paso 1: Generar el Ejecutable

```bash
# Asegúrate de tener el entorno virtual activado
pyinstaller --name="KyoGym" --windowed --onefile --icon=NONE main.py
```

**Explicación de los parámetros:**
- `--name="KyoGym"`: Nombre del ejecutable
- `--windowed`: No muestra consola (aplicación GUI)
- `--onefile`: Todo en un solo archivo .exe
- `--icon=NONE`: Sin icono (puedes agregar uno con `--icon=ruta/icono.ico`)

### Paso 2: Ubicar el Ejecutable

El archivo `KyoGym.exe` se generará en:
```
KyoGym\dist\KyoGym.exe
```

### Paso 3: Crear Acceso Directo en el Escritorio

1. Navega a la carpeta `dist\`
2. Haz clic derecho en `KyoGym.exe`
3. Selecciona "Crear acceso directo"
4. Arrastra el acceso directo a tu escritorio
5. ¡Listo! Haz doble clic para ejecutar

## 📁 Estructura del Proyecto

```
KyoGym/
├── main.py                 # Punto de entrada principal
├── db.py                   # Gestión de base de datos SQLite
├── requirements.txt        # Dependencias
├── services/               # Lógica de negocio (CRUD)
│   ├── __init__.py
│   ├── cliente_service.py
│   ├── membresia_service.py
│   └── pago_service.py
├── views/                  # Interfaces de usuario
│   ├── __init__.py
│   ├── dashboard_view.py
│   ├── membresias_view.py
│   ├── pagos_view.py
│   └── inventario_view.py
└── utils/                  # Constantes y utilidades
    ├── __init__.py
    └── constants.py
```

## 🗄️ Base de Datos

### Tablas

**clientes**
- id (PRIMARY KEY)
- nombre
- telefono
- cedula
- fecha_registro
- activo

**membresias**
- id (PRIMARY KEY)
- cliente_id (FOREIGN KEY → clientes)
- tipo
- fecha_inicio
- fecha_vencimiento
- monto

**pagos**
- id (PRIMARY KEY)
- cliente_id (FOREIGN KEY → clientes)
- membresia_id (FOREIGN KEY → membresias)
- fecha
- monto
- metodo
- concepto

### Estados de Membresía (Calculados Automáticamente)
- **Activa**: Más de 7 días para vencer
- **Por Vencer**: 7 días o menos para vencer
- **Vencida**: Fecha de vencimiento pasada

## 🎯 Uso de la Aplicación

### Dashboard
- Visualiza métricas clave del gimnasio
- Lista de membresías próximas a vencer
- Actualización automática cada 30 segundos

### Membresías
- **Agregar Membresía**: Click en "Agregar Membresía"
- **Filtrar**: Por estado (Activas, Por Vencer, Vencidas)
- Duración por defecto: 30 días

### Pagos
- **Registrar Pago**: Click en "Registrar Pago"
- **Ver Filtros**: Todos, Este Mes, Últimos 50
- Total del mes visible en tiempo real

## 🔧 Desarrollo

### Agregar Nuevos Clientes Manualmente

Puedes agregar clientes desde Python:

```python
from services.cliente_service import crear_cliente
from services.membresia_service import crear_membresia

# Crear cliente
cliente_id = crear_cliente(
    nombre="Juan Pérez",
    telefono="555-1234",
    cedula="12345678"
)

# Crear membresía
crear_membresia(
    cliente_id=cliente_id,
    monto=50.0
)
```

### Personalizar Colores

Edita los colores en las vistas (archivos `views/*.py`):
- `#27ae60`: Verde (Activas)
- `#f39c12`: Naranja (Por Vencer)
- `#e74c3c`: Rojo (Vencidas)
- `#3498db`: Azul (Principal)

## 🐛 Solución de Problemas

### Error: "No module named 'PySide6'"
```bash
pip install PySide6
```

### Error al ejecutar PyInstaller
```bash
pip install --upgrade pyinstaller
```

### La base de datos no se crea
Verifica que tienes permisos de escritura en:
```
%APPDATA%\GymApp\
```

### El .exe no funciona
Ejecuta sin `--windowed` para ver errores:
```bash
pyinstaller --name="KyoGym" --onefile main.py
```

## 📝 Licencia

Proyecto de código abierto para uso educativo y comercial.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Para cambios importantes:
1. Fork del proyecto
2. Crea una rama (`git checkout -b feature/nueva-caracteristica`)
3. Commit de cambios (`git commit -m 'Agregar característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Abre un Pull Request

## 📧 Contacto

Para soporte o consultas sobre el sistema KyoGym.

---

**¡Disfruta gestionando tu gimnasio! 💪**
