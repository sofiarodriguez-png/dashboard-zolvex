# Dashboard ZOLVEX - Resumen del Proyecto

## Descripción General

Dashboard interactivo para visualizar métricas de **ZOLVEX Consumer MLA** con actualización automática 4 veces al día.

## Datos

- **Fuente**: BigQuery - `meli-bi-data.SBOX_COLLECTIONSDA.TLV_CONSUMER_BASE_KPIS_FINAL`
- **Filtros**:
  - `SIT_SITE_ID = 'MLA'` (solo Argentina)
  - `COL_LAST_CALL_CENTER_ASSIGNED = 'ZOLVEX'`
  - `LISTA_GESTION = 1`
- **Periodo**: Últimos 6 meses

## Características Principales

### Métricas Incluidas
1. Clientes Asignados
2. Cobertura Total y CPC
3. Gestiones por Usuario
4. % Clientes Únicos Originados
5. % Monto Originación
6. % Clientes VTA
7. Monto Atribuido VTA
8. Métricas Voice Bot completas

### Filtros Disponibles
- Periodo (mes)
- Tipo de Producto (PL, BNPL, DINERO_PLUS, FASTCHAT)
- Tipo de Segmento (REPEATS, ACTIVATION, CHECKDROP)
- Criterio (búsqueda y selección múltiple)

### Visualizaciones
- Tarjetas KPI con variaciones mensuales
- Tabla de evolución histórica por mes
- Tabla de evolución por criterio específico
- Tabla de métricas Voice Bot
- Gráfico de evolución de coberturas (6 meses)
- Gráfico de monto atribuido VTA

## Archivos del Proyecto

| Archivo | Tamaño | Descripción |
|---------|---------|-------------|
| `generar_dashboard.py` | 74 KB | Script principal que consulta BigQuery y genera el HTML |
| `actualizar_dashboard.py` | 2 KB | Script de actualización y publicación en GitHub |
| `actualizar_dashboard.bat` | 330 B | Ejecutor del script de actualización |
| `tarea_programada.xml` | 2.5 KB | Configuración de tarea programada (horarios) |
| `configurar_tarea_programada.ps1` | 3.1 KB | Script PowerShell para configurar tarea Windows |
| `EJECUTAR_CONFIGURACION.bat` | 536 B | Ejecutor del configurador (requiere admin) |
| `test_conexion.py` | 1.9 KB | Script de prueba de conexión a BigQuery |
| `README.md` | 3 KB | Documentación completa del proyecto |
| `INSTRUCCIONES.txt` | 3.7 KB | Guía paso a paso de configuración |
| `.gitignore` | - | Archivos a ignorar en Git |

## Horarios de Actualización

La tarea programada ejecuta el dashboard en los siguientes horarios:

- **10:00 AM** - Actualización matutina
- **02:00 PM** - Actualización mediodía
- **06:00 PM** - Actualización tarde
- **04:00 AM** - Actualización madrugada

## Flujo de Actualización Automática

```
[Tarea Programada]
    ↓
[actualizar_dashboard.bat]
    ↓
[actualizar_dashboard.py]
    ↓
[1. generar_dashboard.py] → Consulta BigQuery → Genera index.html
    ↓
[2. git add + commit] → Guarda cambios en Git
    ↓
[3. git push] → Publica en GitHub Pages
    ↓
[Dashboard actualizado en vivo]
```

## Diferencias vs Dashboard GEDCO

| Característica | GEDCO | ZOLVEX |
|----------------|-------|--------|
| Países | MLA + MLM | Solo MLA |
| Call Center | GEDCO, GEDCO_MLM | Solo ZOLVEX |
| Secciones | Consumer + Merchant | Solo Consumer |
| Filtro País | Sí | No (siempre MLA) |
| Actualizaciones/día | 4 veces | 4 veces |

## URL del Dashboard

**Producción**: https://sofiarodriguez-png.github.io/dashboard-zolvex/

## Configuración Inicial

### Paso 1: Generar Dashboard
```bash
python generar_dashboard.py
```

### Paso 2: Subir a GitHub
```bash
git add .
git commit -m "Dashboard inicial ZOLVEX"
git push origin main
```

### Paso 3: Activar GitHub Pages
1. Ir a Settings > Pages
2. Source: main branch
3. Save

### Paso 4: Configurar Actualización Automática
1. Ejecutar `EJECUTAR_CONFIGURACION.bat` como Administrador
2. Verificar en Programador de Tareas de Windows

## Verificación

Para probar la conexión antes de generar el dashboard:
```bash
python test_conexion.py
```

## Mantenimiento

### Actualización Manual
```bash
actualizar_dashboard.bat
```

### Verificar Tarea Programada
Windows: Buscar "Programador de tareas" > "Dashboard_ZOLVEX_AutoUpdate"

### Logs
Los logs se muestran en la consola durante la ejecución.

## Estructura del Dashboard HTML

- **Header**: Título y metadata
- **Filtros**: Periodo, Producto, Segmento, Criterio
- **KPIs**: 8 tarjetas principales con variaciones
- **Tablas**:
  - Evolución histórica mensual
  - Evolución por criterio
  - Métricas Voice Bot
- **Gráficos**:
  - Coberturas (líneas)
  - Monto Atribuido VTA (líneas)
- **Modal**: Definiciones de métricas

## Tecnologías

- **Backend**: Python 3.x, BigQuery API
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Gráficos**: Chart.js 4.4.0
- **Automatización**: Windows Task Scheduler
- **Hosting**: GitHub Pages

## Notas Importantes

1. Solo incluye datos de **Consumer MLA**
2. No incluye datos de Merchant
3. No incluye filtro de país (siempre MLA)
4. Idéntico diseño y funcionalidades a GEDCO Consumer
5. Actualización automática cada 6 horas

---

**Fecha de Creación**: 2026-04-10
**Versión**: 1.0
**Autor**: Sofia Rodriguez
