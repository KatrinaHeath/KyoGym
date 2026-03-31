# Validaciones de Campos - Documentación

## Resumen de Cambios

Se han agregado validaciones a los campos de entrada en toda la aplicación KyoGym. Las validaciones se centralizan en el archivo `utils/validators.py` y se aplican en todas las vistas.

## Validadores Disponibles

### 1. **Validador Numérico con Decimales** (`crear_validador_numerico_decimal()`)
- **Uso**: Campos con montos, precios y valores monetarios
- **Acepta**: Números (0-9) y puntos decimales (.)
- **Rechaza**: Letras, caracteres especiales, múltiples puntos
- **Ejemplos válidos**: `10`, `10.5`, `0.99`, `1500.50`
- **Se aplica en**:
  - Membresías: Campo "Monto"
  - Pagos: Campo "Monto"

### 2. **Validador Entero** (`crear_validador_entero()`)
- **Uso**: Campos con cantidades y números sin decimales
- **Acepta**: Solo números (0-9)
- **Rechaza**: Puntos decimales, letras, caracteres especiales
- **Ejemplos válidos**: `10`, `5`, `100`, `999999`
- **Se aplica en**:
  - Pagos: Campo "Cantidad"

### 3. **Validador de Nombre** (`crear_validador_nombre()`)
- **Uso**: Campos con nombres de clientes, gimnasios, etc.
- **Acepta**: Letras (a-z, A-Z), acentos (á, é, í, ó, ú, ñ), espacios, guiones (-), apóstrofos (')
- **Rechaza**: Números, símbolos especiales, caracteres no alfabéticos
- **Ejemplos válidos**: `Juan`, `María García`, `José-Luis`, `Javier O'Connor`
- **Se aplica en**:
  - Clientes: Campo "Nombre"
  - Inventario: Campo "Nombre" (productos)
  - Configuración: Campo "Nombre del Gimnasio"

### 4. **Validador de Teléfono** (`crear_validador_telefono()`)
- **Uso**: Campos con números telefónicos (formato flexible)
- **Acepta**: Números (0-9), espacios, guiones (-), paréntesis (), signo más (+)
- **Rechaza**: Letras, símbolos especiales
- **Ejemplos válidos**: `+50767686213`, `(555) 123-4567`, `555 123 4567`, `+52 123 456 7890`
- **Se aplica en**: No se usa actualmente (reemplazado por formato con guion)

### 4.1 **Teléfono Formateado Dinámico** (`TelefonoFormateadoLineEdit`)
- **Uso**: Campo de teléfono con formato automático XXXX-XXXX
- **Comportamiento especial**:
  - Usuario escribe solo números
  - El guion se inserta automáticamente **después del 4to dígito**
  - Si borra caracteres, el guion se elimina automáticamente
  - Máximo 8 dígitos
- **Ejemplos**:
  - Usuario escribe: `1` → Campo muestra: `1`
  - Usuario escribe: `1234` → Campo muestra: `1234`
  - Usuario escribe: `12345` → Campo muestra: `1234-5`
  - Usuario escribe: `12345678` → Campo muestra: `1234-5678`
  - Usuario borra el guion → Campo muestra automáticamente: `1234`
- **Se aplica en**:
  - Clientes: Campo "Teléfono" (usando `TelefonoFormateadoLineEdit`)
  - Configuración: Campo "Teléfono" (usando `TelefonoFormateadoLineEdit`)

### 5. **Validador de Email** (`crear_validador_email()`)
- **Uso**: Campos con direcciones de correo electrónico
- **Acepta**: Letras, números, puntos (.), guiones (-), guión bajo (_), símbolo (@)
- **Rechaza**: Caracteres especiales no permitidos en email
- **Ejemplos válidos**: `info@kyogym.com`, `user.name@example.com`, `contact-us@app.com`
- **Se aplica en**:
  - Configuración: Campo "Email"

## Archivos Modificados

### Archivos de Vistas:
1. **clientes_view.py**
   - Nombre: Validador de nombre
   - Teléfono: Campo personalizado `TelefonoFormateadoLineEdit` (con guion dinámico)

2. **inventario_view.py**
   - Nombre: Validador de nombre

3. **membresias_view.py**
   - Monto: Validador numérico con decimales

4. **pagos_view.py**
   - Monto: Validador numérico con decimales
   - Cantidad: Validador entero

5. **configuracion_view.py**
   - Nombre del Gimnasio: Validador de nombre
   - Teléfono: Campo personalizado `TelefonoFormateadoLineEdit` (con guion dinámico)
   - Email: Validador de email

### Archivo de Utilidades Creado:
- **utils/validators.py** - Centraliza todas las funciones de validación y la clase `TelefonoFormateadoLineEdit`

## Comportamiento de Validación

- Las validaciones se aplican **en tiempo real** mientras el usuario escribe
- Los validadores **no permiten que se escriban caracteres inválidos**
- El usuario verá un cursor de "no permitido" si intenta escribir un carácter inválido
- Los validadores son **no invasivos**: no interrumpen la experiencia del usuario

## Cómo Usar los Validadores Personalizados

Para agregar un validador a un campo `QLineEdit`:

```python
from utils.validators import crear_validador_nombre, TelefonoFormateadoLineEdit, crear_validador_email

# Crear un campo de nombre
campo_nombre = QLineEdit()
campo_nombre.setValidator(crear_validador_nombre())

# Crear un campo de teléfono formateado dinámico
campo_telefono = TelefonoFormateadoLineEdit()  # Ya tiene el placeholder y lógica de formato

# Crear un campo de email
campo_email = QLineEdit()
campo_email.setValidator(crear_validador_email())
```

### Nota Especial: Teléfono Formateado Dinámico

El teléfono usa la clase personalizada `TelefonoFormateadoLineEdit` que extiende `QLineEdit`. Características:
- ✓ El guion se añade automáticamente después del 4to dígito
- ✓ El guion se elimina automáticamente si el usuario lo borra
- ✓ El usuario solo escribe números
- ✓ Formato garantizado: XXXX-XXXX (8 dígitos totales)
- ✓ No necesita `setInputMask()` ni `setValidator()` adicional

## Campos que Usan QSpinBox y QDoubleSpinBox

Estos campos **ya tienen validación automática** de PySide6:
- **QSpinBox**: Solo acepta números enteros
- **QDoubleSpinBox**: Solo acepta números con decimales
- No requieren validadores adicionales

En la aplicación:
- **Inventario**: Campo "Cantidad" y "Precio" usan estos componentes
