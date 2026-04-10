# Dashboard ZOLVEX - Checklist de Configuración

## Pre-requisitos

- [ ] Python 3.x instalado
- [ ] Git instalado y configurado
- [ ] Acceso a BigQuery configurado
- [ ] Módulo `bigquery_connection` disponible en `C:\Users\sorodriguez\CodigosPy`
- [ ] Repositorio GitHub creado: `dashboard-zolvex`
- [ ] Permisos de administrador en Windows (para tarea programada)

## Verificación de Archivos

- [x] `generar_dashboard.py` - Script principal (74 KB)
- [x] `actualizar_dashboard.py` - Script de actualización (2 KB)
- [x] `actualizar_dashboard.bat` - Batch de actualización (330 B)
- [x] `tarea_programada.xml` - Configuración horarios (2.5 KB)
- [x] `configurar_tarea_programada.ps1` - Configurador PS1 (3.1 KB)
- [x] `EJECUTAR_CONFIGURACION.bat` - Ejecutor configurador (536 B)
- [x] `test_conexion.py` - Test de conexión (1.9 KB)
- [x] `README.md` - Documentación (3 KB)
- [x] `INSTRUCCIONES.txt` - Guía de configuración (3.7 KB)
- [x] `RESUMEN_PROYECTO.md` - Resumen del proyecto
- [x] `.gitignore` - Configuración Git

## Paso 1: Test de Conexión

```bash
python test_conexion.py
```

**Resultado esperado:**
```
[OK] Conexion establecida
[OK] Datos encontrados
[OK] TEST EXITOSO - El dashboard puede generarse correctamente
```

- [ ] Test de conexión exitoso
- [ ] Datos de ZOLVEX encontrados
- [ ] Número de registros > 0

## Paso 2: Generar Dashboard Inicial

```bash
python generar_dashboard.py
```

**Resultado esperado:**
- [ ] Archivo `index.html` creado
- [ ] Sin errores en la ejecución
- [ ] Mensaje: "Dashboard ZOLVEX generado!"

**Verificar en index.html:**
- [ ] Título: "Dashboard ZOLVEX - Consumer MLA"
- [ ] Filtro solo MLA (sin MLM)
- [ ] Solo datos de Consumer (sin Merchant)
- [ ] KPIs visibles
- [ ] Gráficos presentes

## Paso 3: Configurar Git

```bash
git init  # Si no está inicializado
git remote add origin https://github.com/sofiarodriguez-png/dashboard-zolvex.git
git add .
git commit -m "Dashboard inicial ZOLVEX - Consumer MLA"
git push -u origin main
```

**Verificaciones:**
- [ ] Repository creado en GitHub
- [ ] Archivos subidos correctamente
- [ ] Commit visible en GitHub

## Paso 4: Activar GitHub Pages

1. Ir a: `https://github.com/sofiarodriguez-png/dashboard-zolvex`
2. Settings > Pages
3. Source: Deploy from a branch
4. Branch: `main` / `(root)`
5. Save

**Verificaciones:**
- [ ] GitHub Pages activado
- [ ] URL generada: `https://sofiarodriguez-png.github.io/dashboard-zolvex/`
- [ ] Dashboard visible en la URL (esperar 1-2 minutos)

## Paso 5: Configurar Tarea Programada

1. Click derecho en `EJECUTAR_CONFIGURACION.bat`
2. "Ejecutar como administrador"
3. Seguir instrucciones

**Verificaciones:**
- [ ] Script ejecutado sin errores
- [ ] Mensaje: "TAREA PROGRAMADA CONFIGURADA EXITOSAMENTE"
- [ ] Horarios mostrados: 10:00, 14:00, 18:00, 04:00

**Verificar en Windows:**
- [ ] Abrir "Programador de tareas"
- [ ] Buscar: "Dashboard_ZOLVEX_AutoUpdate"
- [ ] Estado: Listo
- [ ] Próxima ejecución programada visible

## Paso 6: Test de Actualización Manual

```bash
actualizar_dashboard.bat
```

**Resultado esperado:**
- [ ] Dashboard generado
- [ ] Commit creado automáticamente
- [ ] Push a GitHub exitoso
- [ ] Mensaje: "ACTUALIZACION COMPLETADA EXITOSAMENTE"

## Paso 7: Verificación Final

**Dashboard en vivo:**
- [ ] Abrir: `https://sofiarodriguez-png.github.io/dashboard-zolvex/`
- [ ] Título correcto: "Dashboard ZOLVEX - Consumer MLA"
- [ ] Datos cargados correctamente
- [ ] Filtros funcionan
- [ ] KPIs se actualizan
- [ ] Gráficos se visualizan
- [ ] Tablas muestran datos

**Filtros esperados:**
- [ ] Periodo (dropdown con meses)
- [ ] Producto (PL, BNPL, DINERO_PLUS, FASTCHAT)
- [ ] Segmento (REPEATS, ACTIVATION, CHECKDROP)
- [ ] Criterio (búsqueda con checkboxes)

**NO debe tener:**
- [ ] ❌ Filtro de País (siempre MLA)
- [ ] ❌ Sección Merchant
- [ ] ❌ Datos de MLM

**Funcionalidades:**
- [ ] Botón "Resetear" funciona
- [ ] Botón "Ver Definiciones" abre modal
- [ ] Hover en KPIs muestra fórmulas
- [ ] Selección de criterio en tabla funciona
- [ ] Gráficos interactivos

## Monitoreo Continuo

**Primera semana:**
- [ ] Lunes 10:00 - Verificar actualización
- [ ] Lunes 14:00 - Verificar actualización
- [ ] Lunes 18:00 - Verificar actualización
- [ ] Martes 04:00 - Verificar actualización

**Verificar en GitHub:**
- [ ] Commits automáticos cada 6 horas
- [ ] Mensajes: "Dashboard actualizado automáticamente - YYYY-MM-DD HH:MM:SS"

## Solución de Problemas

### Error en generar_dashboard.py
- [ ] Verificar conexión a BigQuery
- [ ] Verificar credenciales
- [ ] Verificar que existe la tabla TLV_CONSUMER_BASE_KPIS_FINAL

### Error en actualizar_dashboard.py
- [ ] Verificar que Git está configurado
- [ ] Verificar credenciales de GitHub
- [ ] Verificar que hay cambios para commitear

### Tarea programada no ejecuta
- [ ] Verificar que está habilitada en Programador de Tareas
- [ ] Verificar la ruta del archivo .bat
- [ ] Revisar historial de ejecuciones
- [ ] Verificar permisos

### Dashboard no se actualiza en GitHub Pages
- [ ] Verificar que el commit se hizo correctamente
- [ ] Esperar 1-2 minutos (cache de GitHub)
- [ ] Verificar que GitHub Pages está activo
- [ ] Limpiar cache del navegador

## Contactos y Referencias

**Documentación:**
- README.md - Documentación principal
- INSTRUCCIONES.txt - Guía paso a paso
- RESUMEN_PROYECTO.md - Visión general del proyecto

**URLs importantes:**
- Dashboard: https://sofiarodriguez-png.github.io/dashboard-zolvex/
- Repositorio: https://github.com/sofiarodriguez-png/dashboard-zolvex
- BigQuery: meli-bi-data.SBOX_COLLECTIONSDA.TLV_CONSUMER_BASE_KPIS_FINAL

---

**Fecha de Configuración:** __________
**Configurado por:** __________
**Estado:** ⬜ Pendiente | ⬜ En Progreso | ⬜ Completado
