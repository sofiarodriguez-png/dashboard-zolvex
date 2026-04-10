# Script PowerShell para configurar la tarea programada del Dashboard ZOLVEX
# Debe ejecutarse con permisos de Administrador

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Configurador de Tarea Programada" -ForegroundColor Cyan
Write-Host "Dashboard ZOLVEX - Actualizacion Automatica" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar permisos de administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: Este script necesita permisos de Administrador" -ForegroundColor Red
    Write-Host "Por favor, ejecuta el archivo como Administrador" -ForegroundColor Yellow
    pause
    exit 1
}

# Ruta del archivo XML
$xmlPath = Join-Path $PSScriptRoot "tarea_programada.xml"

if (-not (Test-Path $xmlPath)) {
    Write-Host "ERROR: No se encuentra el archivo tarea_programada.xml" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "Archivo XML encontrado: $xmlPath" -ForegroundColor Green
Write-Host ""

# Nombre de la tarea
$taskName = "Dashboard_ZOLVEX_AutoUpdate"

Write-Host "Verificando si ya existe una tarea con el nombre: $taskName" -ForegroundColor Yellow

# Eliminar tarea existente si la hay
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "Se encontro una tarea existente. Eliminando..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "Tarea anterior eliminada correctamente" -ForegroundColor Green
    Write-Host ""
}

# Registrar la nueva tarea
Write-Host "Registrando nueva tarea programada..." -ForegroundColor Yellow

try {
    Register-ScheduledTask -Xml (Get-Content $xmlPath | Out-String) -TaskName $taskName -Force
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "TAREA PROGRAMADA CONFIGURADA EXITOSAMENTE" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Nombre de la tarea: $taskName" -ForegroundColor Cyan
    Write-Host "Horarios de ejecucion:" -ForegroundColor Cyan
    Write-Host "  - 10:00 AM (todos los dias)" -ForegroundColor White
    Write-Host "  - 02:00 PM (todos los dias)" -ForegroundColor White
    Write-Host "  - 06:00 PM (todos los dias)" -ForegroundColor White
    Write-Host "  - 04:00 AM (todos los dias)" -ForegroundColor White
    Write-Host ""
    Write-Host "Puedes verificar la tarea en el Programador de Tareas de Windows" -ForegroundColor Yellow
    Write-Host ""
} catch {
    Write-Host "ERROR al registrar la tarea:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    pause
    exit 1
}

Write-Host "Presiona cualquier tecla para salir..." -ForegroundColor Gray
pause
