@echo off
echo ===================================
echo Instalando dependencias para sincronización con OneDrive
echo ===================================
echo.

echo Instalando paquetes...
pip install msal openpyxl requests

echo.
echo ===================================
echo Instalación completada
echo ===================================
echo.
echo Ahora puedes ejecutar:
echo   - sync_onedrive.py (para cuentas organizacionales)
echo   - sync_onedrive_personal.py (para cuentas personales)
echo.
pause
