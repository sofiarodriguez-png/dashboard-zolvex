@echo off
REM Script para ejecutar la configuracion de la tarea programada
REM Debe ejecutarse como Administrador

echo ========================================
echo Configuracion de Tarea Programada
echo Dashboard ZOLVEX - Actualizacion Automatica
echo ========================================
echo.
echo IMPORTANTE: Este script necesita permisos de Administrador
echo.
pause

REM Ejecutar PowerShell con permisos de administrador
powershell -ExecutionPolicy Bypass -File "%~dp0configurar_tarea_programada.ps1"

pause
