# Dashboard ZOLVEX - Consumer MLA

Dashboard interactivo para visualizar métricas de ZOLVEX Consumer en MLA (Argentina).

## 🔄 Actualización Automática

Este dashboard se actualiza automáticamente 4 veces al día con los datos más recientes de BigQuery.

## 📊 Ver Dashboard

👉 **[Ver Dashboard en Vivo](https://sofiarodriguez-png.github.io/dashboard-zolvex/)**

## 📈 Métricas Incluidas

- **Clientes Asignados**: Total de clientes únicos asignados
- **Cobertura Total**: % de clientes con al menos una gestión
- **Cobertura CPC**: % de clientes con acción CPC
- **Gestiones por Usuario**: Promedio de gestiones por cliente
- **% Clientes Únicos Originados**: % de clientes que originaron crédito
- **Originados Total**: Total de créditos originados
- **% Clientes VTA**: % de clientes que originaron vía VTA
- **Monto Atribuido VTA**: % del monto total atribuido a VTA

### Métricas Voice Bot

- **Cobertura VB**: Cobertura del Voice Bot
- **Clientes Únicos Originados TEL/VB**
- **Monto Originado TEL/VB**
- **Monto Originado VB/TOTAL**
- **Clientes Únicos Originados VB/TOTAL**

## 🔍 Filtros Disponibles

- Tipo de Producto (DINERO_PLUS, BNPL, PL, FASTCHAT, OTRO)
- Tipo de Segmento (REPEATS, ACTIVATION, CHECKDROP, OTRO)
- Período (selector de mes)
- Criterio (búsqueda y selección múltiple)

## 📊 Gráficos

1. **Evolución de Cobertura y CPC**: Últimos 6 meses
2. **Monto Atribuido VTA**: Evolución histórica

## 🔧 Fuente de Datos

- **Tabla BigQuery**: `meli-bi-data.SBOX_COLLECTIONSDA.TLV_CONSUMER_BASE_KPIS_FINAL`
- **Filtros**:
  - `SIT_SITE_ID = 'MLA'`
  - `COL_LAST_CALL_CENTER_ASSIGNED = 'ZOLVEX'`
  - `LISTA_GESTION = 1`

## ⏰ Horarios de Actualización

El dashboard se actualiza automáticamente en los siguientes horarios:
- **10:00 AM** - Actualización matutina
- **02:00 PM** - Actualización mediodía
- **06:00 PM** - Actualización tarde
- **04:00 AM** - Actualización madrugada

## 🛠️ Configuración de la Tarea Programada

Para configurar la actualización automática:

1. Ejecutar `EJECUTAR_CONFIGURACION.bat` como Administrador
2. El script configurará una tarea programada en Windows
3. La tarea ejecutará automáticamente la actualización en los horarios especificados

## 📁 Archivos del Proyecto

- `generar_dashboard.py`: Script principal que consulta BigQuery y genera el HTML
- `actualizar_dashboard.py`: Script de actualización y publicación automática
- `actualizar_dashboard.bat`: Batch file para ejecutar la actualización
- `tarea_programada.xml`: Configuración de la tarea programada de Windows
- `configurar_tarea_programada.ps1`: Script PowerShell para configurar la tarea
- `EJECUTAR_CONFIGURACION.bat`: Ejecutor del script de configuración
- `index.html`: Dashboard generado (se actualiza automáticamente)

---

*Última actualización: Automática 4 veces al día (10:00, 14:00, 18:00, 04:00)*
