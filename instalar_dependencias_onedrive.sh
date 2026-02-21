#!/bin/bash
echo "==================================="
echo "Instalando dependencias para sincronización con OneDrive"
echo "==================================="
echo ""

echo "Instalando paquetes..."
pip3 install msal openpyxl requests

echo ""
echo "==================================="
echo "Instalación completada"
echo "==================================="
echo ""
echo "Ahora puedes ejecutar:"
echo "  - python3 sync_onedrive.py (para cuentas organizacionales)"
echo "  - python3 sync_onedrive_personal.py (para cuentas personales)"
echo ""
