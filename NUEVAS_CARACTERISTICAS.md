# 🆕 NUEVAS CARACTERÍSTICAS AGREGADAS

## Gestión de Clientes
✅ **Módulo de clientes completo** con los siguientes campos:
- Nombre completo
- Teléfono
- **Sexo** (Masculino/Femenino/Otro)
- **Fecha de nacimiento**

✅ Agregar, editar y eliminar clientes
✅ Búsqueda de clientes en tiempo real
✅ Interfaz amigable con tabla de datos

## Dashboard Mejorado
✅ **Gráfica de distribución de clientes por sexo**
  - Visualización tipo torta con 3 categorías
  - Colores distintivos para cada categoría
  - Actualización automática

✅ **Gráfica de membresías por estado**
  - Membresías Activas (Verde)
  - Membresías Por Vencer (Naranja)
  - Membresías Vencidas (Rojo)

## Sistema de Facturación Automática
✅ **Generación de facturas en PDF** al crear membresías
✅ **Número de factura = ID de membresía** (Primary Key)
✅ **Formato tipo ticket** con:
  - Logo del gimnasio (si existe)
  - Número de factura prominente (#ID)
  - Solo número "63858851" (sin "Zahir Lay")
  - Información del cliente con nombre y teléfono
  - Atendió: Brayan Bernal
  - Detalle del artículo: 1x Mensualidad
  - **Fechas de vigencia de la membresía** (Válido: DD/MM/YYYY - DD/MM/YYYY)
  - Subtotal, Total, Efectivo, Cambio
  - Mensaje "Gracias por su compra"
  - Fecha y hora de emisión en español

✅ Facturas guardadas en: `C:\Users\[Usuario]\KyoGym\Facturas\`
✅ Opción para abrir automáticamente la factura después de crearla

## Migración de Base de Datos
✅ Script de migración `migrar_db.py` que:
  - Agrega campos nuevos sin perder datos existentes
  - Compatible con bases de datos existentes
  - Proceso seguro con rollback en caso de error

## Instrucciones de Uso

### 1. Instalar dependencias
```bash
pip install PySide6 reportlab
```

### 2. Migrar base de datos (si ya tienes datos)
```bash
python migrar_db.py
```

### 3. Ejecutar aplicación
```bash
python main.py
```

### 4. Usar el módulo de Clientes
1. Clic en "👤 Clientes" en el menú lateral
2. Clic en "Agregar Cliente"
3. Llenar formulario con nombre, teléfono, sexo y fecha de nacimiento
4. Guardar

### 5. Crear membresía y generar factura
1. Clic en "👥 Membresías"
2. Clic en "Agregar Membresía"
3. Seleccionar cliente
4. Ingresar fecha de inicio y monto
5. Guardar
6. **Se genera automáticamente la factura en PDF**
7. Opción para abrirla inmediatamente

### 6. Ver gráficas en Dashboard
1. Clic en "🏠 Inicio"
2. Ver gráfica de sexo de clientes
3. Ver gráfica de estado de membresías

## Ubicación de archivos
- Base de datos: `C:\Users\[Usuario]\AppData\Roaming\GymApp\gimnasio.db`
- Facturas: `C:\Users\[Usuario]\KyoGym\Facturas\Factura_[ID].pdf`

## Archivos modificados/creados
- ✅ `db.py` - Tabla clientes actualizada
- ✅ `services/cliente_service.py` - Nuevos campos y función de conteo por sexo
- ✅ `views/clientes_view.py` - **NUEVO** Vista completa de clientes
- ✅ `views/dashboard_view.py` - Agregadas 2 gráficas
- ✅ `views/membresias_view.py` - Generación de facturas
- ✅ `utils/factura_generator.py` - **NUEVO** Generador de PDFs
- ✅ `main.py` - Integración de vista de clientes
- ✅ `requirements.txt` - Agregado reportlab
- ✅ `migrar_db.py` - **NUEVO** Script de migración
