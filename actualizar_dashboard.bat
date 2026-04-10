@echo off
REM Script batch para actualizar el dashboard ZOLVEX

cd /d "%~dp0"
python actualizar_dashboard.py

REM Si hay error, pausar para ver el mensaje
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: La actualizacion fallo. Presiona una tecla para cerrar.
    pause > nul
    exit /b %ERRORLEVEL%
)

exit /b 0
