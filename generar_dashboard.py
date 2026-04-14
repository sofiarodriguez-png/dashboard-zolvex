"""
Dashboard ZOLVEX - Consumer MLA
Consulta datos de BigQuery y genera dashboard HTML
"""
import sys
sys.path.append(r'C:\Users\sorodriguez\CodigosPy')
from bigquery_connection import conectar_bigquery
import pandas as pd
from datetime import datetime
import json

cliente = conectar_bigquery()

print("=" * 80)
print("DASHBOARD ZOLVEX - CONSUMER MLA")
print("=" * 80)
print("\n[INFO] Consultando datos de BigQuery...")

query = """
SELECT
    SIT_SITE_ID AS pais,
    COL_MONTH_ID AS periodo,
    COL_LAST_CALL_CENTER_ASSIGNED AS agencia,
    COL_ASSIGNED_CRITERIA_DESC AS criterio,

    -- Clasificaciones
    CASE
        WHEN UPPER(COL_ASSIGNED_CRITERIA_DESC) LIKE '%DINERO_PLUS%' OR UPPER(COL_ASSIGNED_CRITERIA_DESC) LIKE '%DINERO PLUS%' THEN 'DINERO_PLUS'
        WHEN UPPER(COL_ASSIGNED_CRITERIA_DESC) LIKE '%FASTCHAT%' OR UPPER(COL_ASSIGNED_CRITERIA_DESC) LIKE '%FAST%' THEN 'FASTCHAT'
        WHEN UPPER(COL_ASSIGNED_CRITERIA_DESC) LIKE '%BNPL%' THEN 'BNPL'
        WHEN UPPER(COL_ASSIGNED_CRITERIA_DESC) LIKE '%PL%' AND UPPER(COL_ASSIGNED_CRITERIA_DESC) NOT LIKE '%BNPL%' THEN 'PL'
        ELSE 'OTRO'
    END AS tipo_producto,

    CASE
        WHEN UPPER(COL_ASSIGNED_CRITERIA_DESC) LIKE '%REPEAT%' THEN 'REPEATS'
        WHEN UPPER(COL_ASSIGNED_CRITERIA_DESC) LIKE '%ACTIVATION%' THEN 'ACTIVATION'
        WHEN UPPER(COL_ASSIGNED_CRITERIA_DESC) LIKE '%CHECKOUT DROP%' OR UPPER(COL_ASSIGNED_CRITERIA_DESC) LIKE '%CHECKDROP%' THEN 'CHECKDROP'
        ELSE 'OTRO'
    END AS tipo_segmento,

    -- Base y Cobertura
    SUM(CLIENTES_UNICOS) AS clientes_asignados,
    SUM(CTES_UNICOS_CON_GESTION) AS clientes_con_gestion,
    SUM(CTES_UNICOS_CPC) AS clientes_con_cpc,
    SUM(CTES_UNICOS_OPTIN) AS clientes_con_opt,
    SUM(GESTIONES_TOTALES) AS gestiones_totales,

    -- Propuestas
    SUM(MONTO_PROPUESTAS) AS monto_propuestas,

    -- Originacion Total
    SUM(CTE_UNICOS_ORIGINADOS) AS usuarios_originaron,
    SUM(CANT_CRD_ORIGINADOS) AS cantidad_creditos,
    SUM(MONTO_TOTAL_ORIGINADO) AS monto_originado_total,

    -- Originacion con Gestion
    SUM(CTES_UNICOS_ORIGINADOS_CON_GESTION) AS usuarios_originaron_con_gestion,
    SUM(MONTO_ORIGINADOS_CON_GESTION) AS monto_originado_con_gestion,

    -- Originacion con CPC
    SUM(CTES_UNICOS_ORIGINADOS_CON_CPC) AS usuarios_originaron_con_cpc,
    SUM(MONTO_ORIGINADOS_CON_CPC) AS monto_originado_con_cpc,

    -- Originacion VTA
    SUM(CTE_UNICOS_ORIGINADOS_VTA) AS usuarios_originaron_vta,
    SUM(MONTO_ORIGINADO_USUARIO_VTA) AS monto_originado_vta,
    SUM(MONTO_TOTAL_ORIGINAD_VTA) AS monto_total_vta,

    -- Metricas Voice Bot
    SUM(CTES_UNICOS_CON_OPT_IN_VB) AS clientes_opt_in_vb,
    SUM(CTES_UNICOS_CON_TEL_POST_OPT_IN) AS clientes_tel_post_opt_in,
    SUM(CTES_UNICOS_ORIGINADOS_CON_TEL_POST_OPT_IN) AS clientes_originados_tel_post_opt_in,
    SUM(MONTO_ORIGINADOS_CON_TEL_POST_OPT_IN) AS monto_originados_tel_post_opt_in,
    SUM(MONTO_PROPUESTA_CON_TEL_POST_OPT_IN) AS monto_propuesta_tel_post_opt_in

FROM `meli-bi-data.SBOX_COLLECTIONSDA.TLV_CONSUMER_BASE_KPIS_FINAL`
WHERE
    SIT_SITE_ID = 'MLA'
    AND COL_LAST_CALL_CENTER_ASSIGNED = 'zolvex_mla'
    AND LISTA_GESTION = 1
    AND COL_MONTH_ID >= CAST(FORMAT_DATE('%Y%m', DATE_SUB(CURRENT_DATE(), INTERVAL 6 MONTH)) AS INT64)

GROUP BY pais, periodo, agencia, criterio, tipo_producto, tipo_segmento
ORDER BY periodo DESC, pais
"""

df = cliente.query(query).to_dataframe()
print(f"[OK] {len(df)} registros obtenidos")

if df.empty:
    print("\nNo se encontraron datos!")
    sys.exit(1)

# Procesar datos
df = df.fillna(0)

numeric_cols = ['clientes_asignados', 'clientes_con_gestion', 'clientes_con_cpc', 'clientes_con_opt',
                'gestiones_totales', 'monto_propuestas', 'usuarios_originaron', 'cantidad_creditos',
                'monto_originado_total', 'usuarios_originaron_con_gestion', 'monto_originado_con_gestion',
                'usuarios_originaron_con_cpc', 'monto_originado_con_cpc', 'usuarios_originaron_vta',
                'monto_originado_vta', 'monto_total_vta', 'clientes_opt_in_vb', 'clientes_tel_post_opt_in',
                'clientes_originados_tel_post_opt_in', 'monto_originados_tel_post_opt_in', 'monto_propuesta_tel_post_opt_in']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# Formato periodo
df['periodo_str'] = df['periodo'].astype(str)
df['año'] = df['periodo_str'].str[:4]
df['mes'] = df['periodo_str'].str[4:6]
df['periodo_formato'] = df['año'] + '-' + df['mes']

df = df.sort_values('periodo', ascending=False)

# Obtener lista de periodos disponibles
periodos_disponibles = sorted(df['periodo'].unique(), reverse=True)
ultimo_periodo = periodos_disponibles[0]

print(f"[INFO] Periodos disponibles: {len(periodos_disponibles)}")
print(f"[INFO] Ultimo periodo: {ultimo_periodo}")
print("\n[INFO] Generando dashboard ZOLVEX...")

# Para GitHub Pages, siempre usar index.html
archivo_salida = 'index.html'
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Preparar datos para JavaScript
df_sorted = df.sort_values('periodo', ascending=True)

# Crear lista de periodos formateados para el selector
periodos_lista = [{"value": int(p), "label": f"{str(p)[:4]}-{str(p)[4:6]}"} for p in periodos_disponibles]

# Obtener lista de criterios únicos para el filtro
criterios_unicos = sorted([c for c in df['criterio'].unique() if pd.notna(c) and c != ''])
criterios_lista = [{"value": c, "label": c} for c in criterios_unicos]

# Preparar datos agregados por periodo para el gráfico
df_grafico = df.groupby('periodo').agg({
    'monto_originado_vta': 'sum',
    'monto_originado_total': 'sum'
}).reset_index()
df_grafico['monto_atribuido_pct'] = (df_grafico['monto_originado_vta'] / df_grafico['monto_originado_total'].replace(0, 1) * 100).round(2)
df_grafico = df_grafico.sort_values('periodo')

datos_grafico = df_grafico.to_dict('records')

html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard ZOLVEX - Consumer MLA</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        :root {{
            --color-primary: #009EE3;
            --color-primary-dark: #00396E;
            --color-success: #00A650;
            --color-danger: #D92E2E;
            --color-warning: #FF7A00;
            --color-light-bg: #F5F7FA;
            --color-border: #E0E6ED;
            --color-text: #333;
            --color-text-light: #6B7A8D;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: var(--color-light-bg);
            color: var(--color-text);
            line-height: 1.6;
        }}
        .container {{ max-width: 1800px; margin: 0 auto; background: white; min-height: 100vh; }}

        .header {{
            background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
            color: white;
            padding: 30px 40px;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        .header h1 {{ font-size: 2em; margin-bottom: 10px; }}
        .header-meta {{ font-size: 0.9em; opacity: 0.9; }}

        .filters-section {{
            background: white;
            padding: 20px 40px;
            border-bottom: 2px solid var(--color-border);
            display: flex;
            gap: 20px;
            align-items: center;
            flex-wrap: wrap;
        }}
        .filter-group {{ display: flex; flex-direction: column; gap: 5px; }}
        .filter-group label {{ font-size: 0.75em; text-transform: uppercase; color: var(--color-text-light); font-weight: 600; }}
        .filter-group select {{
            padding: 8px 32px 8px 12px;
            border: 2px solid var(--color-border);
            border-radius: 6px;
            background: white;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
        }}
        .filter-group select:hover {{ border-color: var(--color-primary); }}
        .filter-group select.periodo {{
            border-color: var(--color-primary);
            font-weight: 700;
            background: #E3F2FD;
        }}

        /* Buscador de criterios mejorado */
        .criterio-container {{
            position: relative;
            min-width: 320px;
            max-width: 400px;
        }}
        .criterio-search {{
            width: 100%;
            padding: 8px 12px;
            border: 2px solid var(--color-border);
            border-radius: 6px 6px 0 0;
            font-size: 14px;
            box-sizing: border-box;
        }}
        .criterio-search:focus {{
            outline: none;
            border-color: var(--color-primary);
        }}
        .criterio-list {{
            border: 2px solid var(--color-border);
            border-top: none;
            border-radius: 0 0 6px 6px;
            background: white;
            max-height: 200px;
            overflow-y: auto;
            padding: 8px;
        }}
        .criterio-item {{
            padding: 6px 8px;
            display: flex;
            align-items: center;
            gap: 8px;
            cursor: pointer;
            border-radius: 4px;
            transition: background 0.2s;
        }}
        .criterio-item:hover {{
            background: #f5f5f5;
        }}
        .criterio-item input[type="checkbox"] {{
            cursor: pointer;
            width: 16px;
            height: 16px;
        }}
        .criterio-item label {{
            cursor: pointer;
            flex: 1;
            font-size: 13px;
            margin: 0;
            text-transform: none;
            color: var(--color-text);
            font-weight: normal;
        }}
        .criterio-count {{
            font-size: 11px;
            color: var(--color-text-light);
            padding: 2px 6px;
            background: #f0f0f0;
            border-radius: 3px;
        }}
        .criterio-buttons {{
            display: flex;
            gap: 5px;
            padding: 5px 8px;
            border-bottom: 1px solid #e0e0e0;
        }}
        .criterio-btn {{
            padding: 4px 10px;
            font-size: 11px;
            border: 1px solid #ddd;
            background: white;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .criterio-btn:hover {{
            background: var(--color-primary);
            color: white;
            border-color: var(--color-primary);
        }}

        /* Selector de criterio para tabla (selección única) */
        .criterio-selector-tabla {{
            position: relative;
            min-width: 350px;
        }}
        .criterio-selector-tabla .criterio-search {{
            width: 100%;
            padding: 8px 12px;
            border: 2px solid var(--color-border);
            border-radius: 6px 6px 0 0;
            font-size: 14px;
            box-sizing: border-box;
        }}
        .criterio-selector-tabla .criterio-list {{
            border: 2px solid var(--color-border);
            border-top: none;
            border-radius: 0 0 6px 6px;
            background: white;
            max-height: 250px;
            overflow-y: auto;
            padding: 8px;
        }}
        .criterio-selector-tabla .criterio-item {{
            padding: 6px 8px;
            display: flex;
            align-items: center;
            gap: 8px;
            cursor: pointer;
            border-radius: 4px;
            transition: background 0.2s;
        }}
        .criterio-selector-tabla .criterio-item:hover {{
            background: #f5f5f5;
        }}
        .criterio-selector-tabla .criterio-item.selected {{
            background: #E3F2FD;
            font-weight: 600;
        }}
        .criterio-selector-tabla input[type="radio"] {{
            cursor: pointer;
            width: 16px;
            height: 16px;
        }}
        .criterio-selector-tabla .criterio-item label {{
            cursor: pointer;
            flex: 1;
            font-size: 13px;
            margin: 0;
            text-transform: none;
            color: var(--color-text);
            font-weight: normal;
        }}

        .btn-reset {{
            padding: 8px 16px;
            background: var(--color-danger);
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            font-size: 14px;
        }}
        .btn-definiciones {{
            padding: 8px 16px;
            background: var(--color-primary);
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            font-size: 14px;
            margin-left: auto;
        }}

        .kpis-section {{ padding: 30px 40px; }}
        .section-title {{
            font-size: 1.5em;
            font-weight: 700;
            margin-bottom: 20px;
            color: var(--color-primary-dark);
            padding-bottom: 10px;
            border-bottom: 3px solid var(--color-primary);
        }}
        .kpis-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }}
        .kpi-card {{
            background: white;
            border: 1px solid var(--color-border);
            border-radius: 8px;
            padding: 20px;
            position: relative;
            transition: all 0.3s ease;
            cursor: help;
        }}
        .kpi-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--color-primary);
        }}
        .kpi-card.success::before {{ background: var(--color-success); }}
        .kpi-card.warning::before {{ background: var(--color-warning); }}
        .kpi-card:hover {{ transform: translateY(-4px); box-shadow: 0 8px 20px rgba(0,0,0,0.1); }}
        .kpi-label {{
            font-size: 0.7em;
            text-transform: uppercase;
            color: var(--color-text-light);
            margin-bottom: 8px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        .kpi-info-icon {{
            display: inline-block;
            width: 16px;
            height: 16px;
            background: var(--color-primary);
            color: white;
            border-radius: 50%;
            text-align: center;
            font-size: 12px;
            line-height: 16px;
            cursor: help;
        }}
        .kpi-value {{ font-size: 1.8em; font-weight: 900; margin-bottom: 4px; }}
        .kpi-subtitle {{ font-size: 0.8em; color: var(--color-text-light); margin-bottom: 8px; }}
        .kpi-formula {{
            display: none;
            font-size: 0.75em;
            background: #FFF3E0;
            border-left: 3px solid var(--color-warning);
            padding: 8px;
            margin-top: 8px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            color: #E65100;
        }}
        .kpi-card:hover .kpi-formula {{
            display: block;
        }}
        .kpi-variation {{
            font-size: 0.85em;
            font-weight: 700;
            padding: 4px 8px;
            border-radius: 4px;
            display: inline-block;
        }}
        .kpi-variation.positive {{ background: #E8F5E9; color: var(--color-success); }}
        .kpi-variation.negative {{ background: #FFEBEE; color: var(--color-danger); }}
        .kpi-variation.neutral {{ background: #F5F5F5; color: var(--color-text-light); }}

        .comparativa-section {{
            padding: 30px 40px;
            background: var(--color-light-bg);
        }}
        .tabla-comparativa {{
            width: 100%;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .tabla-comparativa table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .tabla-comparativa th {{
            background: var(--color-primary-dark);
            color: white;
            padding: 16px 12px;
            text-align: left;
            font-size: 0.85em;
            font-weight: 600;
            text-transform: uppercase;
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        .tabla-comparativa td {{
            padding: 14px 12px;
            border-bottom: 1px solid var(--color-border);
            font-size: 0.9em;
        }}
        .tabla-comparativa tr:hover {{
            background: #F5F7FA;
        }}
        .tabla-comparativa tr.selected {{
            background: #E3F2FD;
            font-weight: 600;
        }}
        .tabla-comparativa .numero {{
            text-align: right;
            font-family: 'Courier New', monospace;
            font-weight: 500;
        }}
        .tabla-comparativa .porcentaje {{
            text-align: right;
            font-weight: 600;
        }}
        .tabla-comparativa .periodo-col {{
            font-weight: 700;
            color: var(--color-primary);
        }}

        .graficos-section {{
            padding: 30px 40px;
            background: white;
        }}
        .chart-container {{
            position: relative;
            height: 400px;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        /* Modal de definiciones */
        .modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            overflow-y: auto;
        }}
        .modal.show {{
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        .modal-content {{
            background: white;
            border-radius: 12px;
            max-width: 900px;
            width: 100%;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        .modal-header {{
            background: var(--color-primary-dark);
            color: white;
            padding: 20px 30px;
            border-radius: 12px 12px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .modal-header h2 {{
            font-size: 1.5em;
            margin: 0;
        }}
        .modal-close {{
            background: none;
            border: none;
            color: white;
            font-size: 28px;
            cursor: pointer;
            padding: 0;
            width: 30px;
            height: 30px;
            line-height: 30px;
        }}
        .modal-body {{
            padding: 30px;
        }}
        .definicion-item {{
            margin-bottom: 25px;
            padding: 15px;
            background: #F5F7FA;
            border-radius: 8px;
            border-left: 4px solid var(--color-primary);
        }}
        .definicion-item h3 {{
            color: var(--color-primary-dark);
            font-size: 1.1em;
            margin-bottom: 10px;
        }}
        .definicion-formula {{
            background: #FFF3E0;
            padding: 10px 15px;
            border-radius: 6px;
            font-family: 'Courier New', monospace;
            font-size: 0.95em;
            color: #E65100;
            margin: 10px 0;
            border-left: 3px solid var(--color-warning);
        }}
        .definicion-desc {{
            color: var(--color-text-light);
            font-size: 0.9em;
            margin-top: 8px;
        }}
        .definicion-campos {{
            margin-top: 10px;
            font-size: 0.85em;
            color: var(--color-text-light);
        }}
        .definicion-campos strong {{
            color: var(--color-text);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Dashboard ZOLVEX - Consumer MLA</h1>
            <div class="header-meta">
                Actualizado: {timestamp} |
                Registros: {len(df)} |
                Filtro: MLA + zolvex_mla
            </div>
        </div>

        <div class="filters-section">
            <div class="filter-group">
                <label>Periodo</label>
                <select id="filtroPeriodo" class="periodo" onchange="aplicarFiltros()">
                    <!-- Se llena dinámicamente -->
                </select>
            </div>
            <div class="filter-group">
                <label>Producto</label>
                <select id="filtroProducto" onchange="filtrarCriteriosAutomaticamente()">
                    <option value="TODOS">Todos</option>
                    <option value="PL">PL</option>
                    <option value="BNPL">BNPL</option>
                    <option value="DINERO_PLUS">DINERO_PLUS</option>
                    <option value="FASTCHAT">FASTCHAT</option>
                </select>
            </div>
            <div class="filter-group">
                <label>Segmento</label>
                <select id="filtroSegmento" onchange="filtrarCriteriosAutomaticamente()">
                    <option value="TODOS">Todos</option>
                    <option value="REPEATS">REPEATS</option>
                    <option value="ACTIVATION">ACTIVATION</option>
                    <option value="CHECKDROP">CHECKDROP</option>
                </select>
            </div>
            <div class="filter-group criterio-container">
                <label>🔍 Criterio <span id="criterioCount" class="criterio-count"></span></label>
                <input type="text" id="criterioBuscador" class="criterio-search" placeholder="Buscar criterio (ej: PL, REPEATS, etc.)" oninput="filtrarCriteriosLista()">
                <div class="criterio-list">
                    <div class="criterio-buttons">
                        <button class="criterio-btn" onclick="seleccionarTodosCriterios()">✓ Todos</button>
                        <button class="criterio-btn" onclick="deseleccionarTodosCriterios()">✗ Ninguno</button>
                    </div>
                    <div id="criterioLista">
                        <!-- Se llena dinámicamente con checkboxes -->
                    </div>
                </div>
            </div>
            <button class="btn-reset" onclick="resetFiltros()">Resetear</button>
            <button class="btn-definiciones" onclick="mostrarDefiniciones()">📖 Ver Definiciones</button>
        </div>

        <div class="kpis-section">
            <h2 class="section-title" id="tituloKPIs">Métricas Principales</h2>
            <div id="kpisContainer" class="kpis-grid"></div>
        </div>

        <div class="comparativa-section">
            <h2 class="section-title">Evolución Histórica por Mes</h2>
            <div class="tabla-comparativa">
                <table id="tablaComparativa">
                    <thead>
                        <tr>
                            <th>Periodo</th>
                            <th class="numero">Clientes</th>
                            <th class="porcentaje">Cobertura %</th>
                            <th class="porcentaje">CPC %</th>
                            <th class="numero">Gest/Usuario</th>
                            <th class="porcentaje">Originados Total %</th>
                            <th class="porcentaje">% Monto Orig</th>
                            <th class="porcentaje">% Monto CPC</th>
                            <th class="porcentaje">% Monto Atrib VTA</th>
                            <th class="porcentaje">% Clt Orig VTA/Total Orig</th>
                        </tr>
                    </thead>
                    <tbody id="tablaBody">
                        <!-- Se llena dinámicamente -->
                    </tbody>
                </table>
            </div>
        </div>

        <div class="comparativa-section" style="padding-top: 0;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px; gap: 20px;">
                <h2 class="section-title" style="margin: 0;">Evolución por Criterio</h2>
                <div class="filter-group criterio-selector-tabla" style="margin: 0;">
                    <label>🔍 Seleccionar Criterio:</label>
                    <input type="text" id="criterioBuscadorTabla" class="criterio-search" placeholder="Buscar criterio..." oninput="filtrarCriteriosTabla()">
                    <div class="criterio-list" id="criterioListaTabla">
                        <!-- Se llena dinámicamente con radio buttons -->
                    </div>
                </div>
            </div>
            <div class="tabla-comparativa">
                <table id="tablaPorCriterio">
                    <thead>
                        <tr>
                            <th>Periodo</th>
                            <th class="numero">Clientes</th>
                            <th class="porcentaje">Cobertura %</th>
                            <th class="porcentaje">CPC %</th>
                            <th class="numero">Gest/Usuario</th>
                            <th class="porcentaje">Originados Total %</th>
                            <th class="porcentaje">% Monto Orig</th>
                            <th class="porcentaje">% Monto CPC</th>
                            <th class="porcentaje">% Monto Atrib VTA</th>
                            <th class="porcentaje">% Clt Orig VTA/Total Orig</th>
                        </tr>
                    </thead>
                    <tbody id="tablaCriterioBody">
                        <!-- Se llena dinámicamente -->
                    </tbody>
                </table>
            </div>
        </div>

        <div class="comparativa-section" style="padding-top: 0;">
            <h2 class="section-title">Métricas Voice Bot (OPT-IN VB)</h2>
            <div class="tabla-comparativa">
                <table id="tablaVoiceBot">
                    <thead>
                        <tr>
                            <th>Métrica</th>
                            <th class="numero" id="vb-col-1">-</th>
                            <th class="numero" id="vb-col-2">-</th>
                            <th class="numero" id="vb-col-3">-</th>
                            <th class="numero" id="vb-col-4">-</th>
                        </tr>
                    </thead>
                    <tbody id="tablaVBBody">
                        <!-- Se llena dinámicamente -->
                    </tbody>
                </table>
            </div>
        </div>

        <div class="graficos-section">
            <h2 class="section-title">Evolución de Coberturas - Últimos 6 Meses</h2>
            <div class="chart-container">
                <canvas id="chartCoberturas"></canvas>
            </div>
        </div>

        <div class="graficos-section" style="padding-top: 0;">
            <h2 class="section-title">Monto Atribuido VTA - Evolución</h2>
            <div class="chart-container">
                <canvas id="chartMontoAtribuido"></canvas>
            </div>
        </div>

        <div class="graficos-section" style="padding-top: 0;">
            <h2 class="section-title">💰 Ticket Promedio - Evolución</h2>
            <div style="max-width: 1000px; margin: 0 auto; background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%); padding: 25px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
                <div style="height: 350px; position: relative;">
                    <canvas id="chartTicketPromedio"></canvas>
                </div>
                <div style="margin-top: 20px; padding: 18px; background: white; border-radius: 8px; border-left: 4px solid #2196F3; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                    <div style="font-size: 13px; color: #555; line-height: 1.8;">
                        <strong style="color: #333; font-size: 14px;">📊 Definiciones:</strong><br>
                        <div style="margin-top: 8px;">
                            <span style="display: inline-block; width: 12px; height: 12px; background: #2196F3; border-radius: 2px; margin-right: 8px;"></span>
                            <strong>Ticket Promedio Total:</strong> Monto Total Originado ÷ Usuarios que Originaron
                        </div>
                        <div style="margin-top: 6px;">
                            <span style="display: inline-block; width: 12px; height: 12px; background: #FF7A00; border-radius: 2px; margin-right: 8px;"></span>
                            <strong>Ticket Promedio VTA (Usuario):</strong> Monto Originado VTA ÷ Usuarios que Originaron VTA
                        </div>
                        <div style="margin-top: 6px;">
                            <span style="display: inline-block; width: 12px; height: 12px; background: #4CAF50; border-radius: 2px; margin-right: 8px;"></span>
                            <strong>Ticket Promedio Atribución VTA:</strong> Monto Total VTA ÷ Usuarios que Originaron VTA
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal de Definiciones -->
    <div id="modalDefiniciones" class="modal" onclick="cerrarModal(event)">
        <div class="modal-content" onclick="event.stopPropagation()">
            <div class="modal-header">
                <h2>Definiciones de Métricas</h2>
                <button class="modal-close" onclick="cerrarModal()">&times;</button>
            </div>
            <div class="modal-body">
                <div class="definicion-item">
                    <h3>Clientes Asignados</h3>
                    <div class="definicion-formula">SUM(CLIENTES_UNICOS)</div>
                    <div class="definicion-desc">Total de clientes únicos asignados a ZOLVEX en el período.</div>
                </div>

                <div class="definicion-item">
                    <h3>Cobertura Total</h3>
                    <div class="definicion-formula">(CTES_UNICOS_CON_GESTION / CLIENTES_UNICOS) × 100</div>
                    <div class="definicion-desc">Porcentaje de clientes que tuvieron al menos una gestión.</div>
                </div>

                <div class="definicion-item">
                    <h3>Cobertura CPC</h3>
                    <div class="definicion-formula">(CTES_UNICOS_CPC / CLIENTES_UNICOS) × 100</div>
                    <div class="definicion-desc">Porcentaje de clientes con al menos una acción CPC.</div>
                </div>

                <div class="definicion-item">
                    <h3>Gestiones por Usuario</h3>
                    <div class="definicion-formula">GESTIONES_TOTALES / CLIENTES_UNICOS</div>
                    <div class="definicion-desc">Promedio de gestiones por cliente asignado.</div>
                </div>

                <div class="definicion-item">
                    <h3>% Clientes Únicos Originados</h3>
                    <div class="definicion-formula">(CTE_UNICOS_ORIGINADOS / CLIENTES_UNICOS) × 100</div>
                    <div class="definicion-desc">Porcentaje de clientes que originaron al menos un crédito.</div>
                </div>

                <div class="definicion-item">
                    <h3>% Monto Originación</h3>
                    <div class="definicion-formula">(MONTO_TOTAL_ORIGINADO / MONTO_PROPUESTAS) × 100</div>
                    <div class="definicion-desc">Porcentaje del monto propuesto que se originó.</div>
                </div>

                <div class="definicion-item">
                    <h3>% Clientes VTA</h3>
                    <div class="definicion-formula">(CTE_UNICOS_ORIGINADOS_VTA / CLIENTES_UNICOS) × 100</div>
                    <div class="definicion-desc">Porcentaje de clientes que originaron mediante VTA.</div>
                </div>

                <div class="definicion-item">
                    <h3>Monto Atribuido VTA</h3>
                    <div class="definicion-formula">(MONTO_ORIGINADO_USUARIO_VTA / MONTO_TOTAL_ORIGINADO) × 100</div>
                    <div class="definicion-desc">Porcentaje del monto total originado que corresponde a VTA (Venta Telefónica Asistida).</div>
                    <div class="definicion-campos">
                        <strong>Numerador:</strong> MONTO_ORIGINADO_USUARIO_VTA<br>
                        <strong>Denominador:</strong> MONTO_TOTAL_ORIGINADO
                    </div>
                </div>

                <div class="definicion-item" style="background: #E3F2FD; border-left-color: var(--color-primary);">
                    <h3>📊 Fuente de Datos</h3>
                    <div class="definicion-desc">
                        <strong>Tabla:</strong> meli-bi-data.SBOX_COLLECTIONSDA.TLV_CONSUMER_BASE_KPIS_FINAL<br>
                        <strong>Filtros:</strong> SIT_SITE_ID = 'MLA' AND COL_LAST_CALL_CENTER_ASSIGNED = 'zolvex_mla' AND LISTA_GESTION = 1
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const datosCompletos = {json.dumps(df_sorted.to_dict('records'))};
        const periodosDisponibles = {json.dumps(periodos_lista)};
        const criteriosDisponibles = {json.dumps(criterios_lista)};
        const datosGrafico = {json.dumps(datos_grafico)};
        let periodoSeleccionado = {ultimo_periodo};
        let chartMontoAtribuido = null;
        let chartCoberturas = null;
        let chartTicketPromedio = null;

        function mostrarDefiniciones() {{
            document.getElementById('modalDefiniciones').classList.add('show');
        }}

        function cerrarModal(event) {{
            if (!event || event.target.id === 'modalDefiniciones') {{
                document.getElementById('modalDefiniciones').classList.remove('show');
            }}
        }}

        function filtrarCriteriosLista() {{
            const searchText = document.getElementById('criterioBuscador').value.toLowerCase();
            const items = document.querySelectorAll('#criterioLista .criterio-item');

            items.forEach(item => {{
                const criterioText = item.dataset.criterio;
                if (criterioText.includes(searchText)) {{
                    item.style.display = 'flex';
                }} else {{
                    item.style.display = 'none';
                }}
            }});
        }}

        function filtrarCriteriosTabla() {{
            const searchText = document.getElementById('criterioBuscadorTabla').value.toLowerCase();
            const items = document.querySelectorAll('#criterioListaTabla .criterio-item');

            items.forEach(item => {{
                const criterioText = item.dataset.criterio;
                if (criterioText.includes(searchText)) {{
                    item.style.display = 'flex';
                }} else {{
                    item.style.display = 'none';
                }}
            }});
        }}

        function seleccionarTodosCriterios() {{
            const checkboxes = document.querySelectorAll('#criterioLista input[type="checkbox"]');
            checkboxes.forEach(cb => cb.checked = true);
            aplicarFiltros();
        }}

        function deseleccionarTodosCriterios() {{
            const checkboxes = document.querySelectorAll('#criterioLista input[type="checkbox"]');
            checkboxes.forEach(cb => cb.checked = false);
            aplicarFiltros();
        }}

        function filtrarCriteriosAutomaticamente() {{
            const producto = document.getElementById('filtroProducto').value;
            const segmento = document.getElementById('filtroSegmento').value;

            // Si todos están en "TODOS", marcar todos los criterios
            if (producto === 'TODOS' && segmento === 'TODOS') {{
                seleccionarTodosCriterios();
                return;
            }}

            // Construir términos de búsqueda
            const terminos = [];
            if (producto !== 'TODOS') terminos.push(producto.toLowerCase());
            if (segmento !== 'TODOS') terminos.push(segmento.toLowerCase());

            // Marcar solo los criterios que contienen TODOS los términos como PALABRAS COMPLETAS
            const checkboxes = document.querySelectorAll('#criterioLista input[type="checkbox"]');
            checkboxes.forEach(cb => {{
                const criterioText = cb.value.toLowerCase();
                // Dividir el criterio en palabras usando underscore como separador
                const palabrasCriterio = criterioText.split('_');

                // Verificar que TODOS los términos existan como palabras completas
                const contieneTodasLasPalabras = terminos.every(termino =>
                    palabrasCriterio.includes(termino)
                );
                cb.checked = contieneTodasLasPalabras;
            }});

            aplicarFiltros();
        }}

        function inicializarFiltros() {{
            const selectPeriodo = document.getElementById('filtroPeriodo');
            periodosDisponibles.forEach(p => {{
                const option = document.createElement('option');
                option.value = p.value;
                option.text = p.label;
                selectPeriodo.appendChild(option);
            }});
            selectPeriodo.value = periodoSeleccionado;

            // Inicializar filtro de criterio con checkboxes
            const criterioLista = document.getElementById('criterioLista');
            criteriosDisponibles.forEach((c, index) => {{
                const div = document.createElement('div');
                div.className = 'criterio-item';
                div.dataset.criterio = c.value.toLowerCase();

                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.id = `criterio-${{index}}`;
                checkbox.value = c.value;
                checkbox.checked = true; // Por defecto todos seleccionados
                checkbox.onchange = aplicarFiltros;

                const label = document.createElement('label');
                label.htmlFor = `criterio-${{index}}`;
                label.textContent = c.label;

                div.appendChild(checkbox);
                div.appendChild(label);
                div.onclick = function(e) {{
                    if (e.target.tagName !== 'INPUT') {{
                        checkbox.checked = !checkbox.checked;
                        aplicarFiltros();
                    }}
                }};

                criterioLista.appendChild(div);
            }});

            // Inicializar selector de criterio para tabla (radio buttons)
            const criterioListaTabla = document.getElementById('criterioListaTabla');
            criteriosDisponibles.forEach((c, index) => {{
                const div = document.createElement('div');
                div.className = 'criterio-item';
                div.dataset.criterio = c.value.toLowerCase();

                const radio = document.createElement('input');
                radio.type = 'radio';
                radio.name = 'criterioTabla';
                radio.id = `criterioTabla-${{index}}`;
                radio.value = c.value;
                radio.onchange = actualizarTablaPorCriterio;

                // Seleccionar el primer criterio por defecto
                if (index === 0) {{
                    radio.checked = true;
                    div.classList.add('selected');
                }}

                const label = document.createElement('label');
                label.htmlFor = `criterioTabla-${{index}}`;
                label.textContent = c.label;

                div.appendChild(radio);
                div.appendChild(label);
                div.onclick = function(e) {{
                    if (e.target.tagName !== 'INPUT') {{
                        radio.checked = true;
                        // Actualizar clases selected
                        document.querySelectorAll('#criterioListaTabla .criterio-item').forEach(item => item.classList.remove('selected'));
                        div.classList.add('selected');
                        actualizarTablaPorCriterio();
                    }}
                }};

                criterioListaTabla.appendChild(div);
            }});
        }}

        function filtrarDatos() {{
            const producto = document.getElementById('filtroProducto').value;
            const segmento = document.getElementById('filtroSegmento').value;

            // Obtener criterios seleccionados (checkboxes)
            const checkboxes = document.querySelectorAll('#criterioLista input[type="checkbox"]:checked');
            const criteriosSeleccionados = Array.from(checkboxes).map(cb => cb.value);

            return datosCompletos.filter(d => {{
                if (producto !== 'TODOS' && d.tipo_producto !== producto) return false;
                if (segmento !== 'TODOS' && d.tipo_segmento !== segmento) return false;

                // Filtro de criterio (si hay selección, debe estar en la lista)
                if (criteriosSeleccionados.length > 0 && !criteriosSeleccionados.includes(d.criterio)) return false;

                return true;
            }});
        }}

        function aplicarFiltros() {{
            periodoSeleccionado = parseInt(document.getElementById('filtroPeriodo').value);

            // Actualizar contador de criterios seleccionados
            const checkboxes = document.querySelectorAll('#criterioLista input[type="checkbox"]');
            const seleccionados = Array.from(checkboxes).filter(cb => cb.checked).length;
            const total = checkboxes.length;
            document.getElementById('criterioCount').textContent = `${{seleccionados}}/${{total}}`;

            actualizarKPIs();
            actualizarTablaComparativa();
            actualizarTablaPorCriterio();
            actualizarTablaVoiceBot();
            actualizarGraficoCoberturas();
            actualizarGraficoMontoAtribuido();
            actualizarGraficoTicketPromedio();
        }}

        function resetFiltros() {{
            document.getElementById('filtroPeriodo').value = periodosDisponibles[0].value;
            document.getElementById('filtroProducto').value = 'TODOS';
            document.getElementById('filtroSegmento').value = 'TODOS';

            // Limpiar buscador y seleccionar todos los criterios
            document.getElementById('criterioBuscador').value = '';
            const checkboxes = document.querySelectorAll('#criterioLista input[type="checkbox"]');
            checkboxes.forEach(cb => cb.checked = true);

            // Mostrar todos los items
            filtrarCriteriosLista();

            aplicarFiltros();
        }}

        function actualizarKPIs() {{
            const datos = filtrarDatos();
            const datosActual = datos.filter(d => d.periodo === periodoSeleccionado);

            const periodosOrdenados = [...new Set(datos.map(d => d.periodo))].sort((a, b) => b - a);
            const indexActual = periodosOrdenados.indexOf(periodoSeleccionado);
            const periodoAnterior = indexActual < periodosOrdenados.length - 1 ? periodosOrdenados[indexActual + 1] : null;
            const datosAnterior = periodoAnterior ? datos.filter(d => d.periodo === periodoAnterior) : [];

            const periodoLabel = periodosDisponibles.find(p => p.value === periodoSeleccionado)?.label || '';
            document.getElementById('tituloKPIs').textContent = `Métricas Principales - ${{periodoLabel}}`;

            const base = datosActual.reduce((s, d) => s + d.clientes_asignados, 0);
            const gestionados = datosActual.reduce((s, d) => s + d.clientes_con_gestion, 0);
            const cpc = datosActual.reduce((s, d) => s + d.clientes_con_cpc, 0);
            const gestiones = datosActual.reduce((s, d) => s + d.gestiones_totales, 0);
            const propuestas = datosActual.reduce((s, d) => s + d.monto_propuestas, 0);
            const originaron = datosActual.reduce((s, d) => s + d.usuarios_originaron, 0);
            const origVTA = datosActual.reduce((s, d) => s + d.usuarios_originaron_vta, 0);
            const montoTotal = datosActual.reduce((s, d) => s + d.monto_originado_total, 0);
            const montoVTA = datosActual.reduce((s, d) => s + d.monto_originado_vta, 0);

            const baseAnt = datosAnterior.reduce((s, d) => s + d.clientes_asignados, 0);
            const gestionadosAnt = datosAnterior.reduce((s, d) => s + d.clientes_con_gestion, 0);
            const cpcAnt = datosAnterior.reduce((s, d) => s + d.clientes_con_cpc, 0);
            const originaronAnt = datosAnterior.reduce((s, d) => s + d.usuarios_originaron, 0);
            const origVTAAnt = datosAnterior.reduce((s, d) => s + d.usuarios_originaron_vta, 0);
            const montoTotalAnt = datosAnterior.reduce((s, d) => s + d.monto_originado_total, 0);
            const montoVTAAnt = datosAnterior.reduce((s, d) => s + d.monto_originado_vta, 0);

            const cobertura = base > 0 ? (gestionados * 100 / base).toFixed(2) : 0;
            const pctCPC = base > 0 ? (cpc * 100 / base).toFixed(2) : 0;
            const gestPorUsuario = base > 0 ? (gestiones / base).toFixed(2) : 0;
            const pctCltOrig = base > 0 ? (originaron * 100 / base).toFixed(2) : 0;
            const pctOriginacion = propuestas > 0 ? (montoTotal * 100 / propuestas).toFixed(2) : 0;
            const pctCltVTA = base > 0 ? (origVTA * 100 / base).toFixed(2) : 0;
            const montoAtribuido = montoTotal > 0 ? (montoVTA * 100 / montoTotal).toFixed(2) : 0;

            const coberturaAnt = baseAnt > 0 ? (gestionadosAnt * 100 / baseAnt).toFixed(2) : 0;
            const pctCPCAnt = baseAnt > 0 ? (cpcAnt * 100 / baseAnt).toFixed(2) : 0;
            const pctCltOrigAnt = baseAnt > 0 ? (originaronAnt * 100 / baseAnt).toFixed(2) : 0;
            const pctCltVTAAnt = baseAnt > 0 ? (origVTAAnt * 100 / baseAnt).toFixed(2) : 0;
            const montoAtribuidoAnt = montoTotalAnt > 0 ? (montoVTAAnt * 100 / montoTotalAnt).toFixed(2) : 0;

            function calcVar(actual, anterior) {{
                if (anterior === 0) return {{ diff: 0, pct: 0, clase: 'neutral' }};
                const diff = (actual - anterior).toFixed(2);
                const pct = ((actual - anterior) * 100 / anterior).toFixed(2);
                const clase = diff > 0 ? 'positive' : diff < 0 ? 'negative' : 'neutral';
                const signo = diff > 0 ? '+' : '';
                return {{ diff: signo + diff, pct: signo + pct, clase }};
            }}

            const varCobertura = calcVar(parseFloat(cobertura), parseFloat(coberturaAnt));
            const varCPC = calcVar(parseFloat(pctCPC), parseFloat(pctCPCAnt));
            const varCltOrig = calcVar(parseFloat(pctCltOrig), parseFloat(pctCltOrigAnt));
            const varCltVTA = calcVar(parseFloat(pctCltVTA), parseFloat(pctCltVTAAnt));
            const varMontoAtribuido = calcVar(parseFloat(montoAtribuido), parseFloat(montoAtribuidoAnt));

            document.getElementById('kpisContainer').innerHTML = `
                <div class="kpi-card success">
                    <div class="kpi-label">Clientes Asignados <span class="kpi-info-icon">i</span></div>
                    <div class="kpi-value">${{base.toLocaleString()}}</div>
                    <div class="kpi-subtitle">Base total del periodo</div>
                    <div class="kpi-formula">= SUM(CLIENTES_UNICOS)</div>
                </div>
                <div class="kpi-card success">
                    <div class="kpi-label">Cobertura Total <span class="kpi-info-icon">i</span></div>
                    <div class="kpi-value">${{cobertura}}%</div>
                    <div class="kpi-subtitle">${{gestionados.toLocaleString()}} clientes con gestion</div>
                    ${{periodoAnterior ? `<div class="kpi-variation ${{varCobertura.clase}}">${{varCobertura.diff}} pp (${{varCobertura.pct}}%) vs mes anterior</div>` : ''}}
                    <div class="kpi-formula">= (CTES_UNICOS_CON_GESTION / CLIENTES_UNICOS) × 100</div>
                </div>
                <div class="kpi-card success">
                    <div class="kpi-label">Cobertura CPC <span class="kpi-info-icon">i</span></div>
                    <div class="kpi-value">${{pctCPC}}%</div>
                    <div class="kpi-subtitle">${{cpc.toLocaleString()}} clientes con CPC</div>
                    ${{periodoAnterior ? `<div class="kpi-variation ${{varCPC.clase}}">${{varCPC.diff}} pp (${{varCPC.pct}}%) vs mes anterior</div>` : ''}}
                    <div class="kpi-formula">= (CTES_UNICOS_CPC / CLIENTES_UNICOS) × 100</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Gestiones por Usuario <span class="kpi-info-icon">i</span></div>
                    <div class="kpi-value">${{gestPorUsuario}}</div>
                    <div class="kpi-subtitle">${{gestiones.toLocaleString()}} gestiones totales</div>
                    <div class="kpi-formula">= GESTIONES_TOTALES / CLIENTES_UNICOS</div>
                </div>
                <div class="kpi-card warning">
                    <div class="kpi-label">% Clientes Únicos Originados <span class="kpi-info-icon">i</span></div>
                    <div class="kpi-value">${{pctCltOrig}}%</div>
                    <div class="kpi-subtitle">${{originaron.toLocaleString()}} usuarios originaron</div>
                    ${{periodoAnterior ? `<div class="kpi-variation ${{varCltOrig.clase}}">${{varCltOrig.diff}} pp (${{varCltOrig.pct}}%) vs mes anterior</div>` : ''}}
                    <div class="kpi-formula">= (CTE_UNICOS_ORIGINADOS / CLIENTES_UNICOS) × 100</div>
                </div>
                <div class="kpi-card warning">
                    <div class="kpi-label">% Monto Originación <span class="kpi-info-icon">i</span></div>
                    <div class="kpi-value">${{pctOriginacion}}%</div>
                    <div class="kpi-subtitle">$$${{(montoTotal/1000000).toFixed(1)}}M de $$${{(propuestas/1000000).toFixed(1)}}M</div>
                    <div class="kpi-formula">= (MONTO_TOTAL_ORIGINADO / MONTO_PROPUESTAS) × 100</div>
                </div>
                <div class="kpi-card warning">
                    <div class="kpi-label">% Clientes VTA <span class="kpi-info-icon">i</span></div>
                    <div class="kpi-value">${{pctCltVTA}}%</div>
                    <div class="kpi-subtitle">${{origVTA.toLocaleString()}} usuarios VTA</div>
                    ${{periodoAnterior ? `<div class="kpi-variation ${{varCltVTA.clase}}">${{varCltVTA.diff}} pp (${{varCltVTA.pct}}%) vs mes anterior</div>` : ''}}
                    <div class="kpi-formula">= (CTE_UNICOS_ORIGINADOS_VTA / CLIENTES_UNICOS) × 100</div>
                </div>
                <div class="kpi-card warning">
                    <div class="kpi-label">Monto Atribuido VTA <span class="kpi-info-icon">i</span></div>
                    <div class="kpi-value">${{montoAtribuido}}%</div>
                    <div class="kpi-subtitle">$$${{(montoVTA/1000000).toFixed(1)}}M de $$${{(montoTotal/1000000).toFixed(1)}}M</div>
                    ${{periodoAnterior ? `<div class="kpi-variation ${{varMontoAtribuido.clase}}">${{varMontoAtribuido.diff}} pp (${{varMontoAtribuido.pct}}%) vs mes anterior</div>` : ''}}
                    <div class="kpi-formula">= (MONTO_ORIGINADO_USUARIO_VTA / MONTO_TOTAL_ORIGINADO) × 100</div>
                </div>
            `;
        }}

        function actualizarTablaComparativa() {{
            const datos = filtrarDatos();
            const periodosOrdenados = [...new Set(datos.map(d => d.periodo))].sort((a, b) => b - a);

            let html = '';
            periodosOrdenados.forEach(periodo => {{
                const datosPeriodo = datos.filter(d => d.periodo === periodo);

                const base = datosPeriodo.reduce((s, d) => s + d.clientes_asignados, 0);
                const gestionados = datosPeriodo.reduce((s, d) => s + d.clientes_con_gestion, 0);
                const cpc = datosPeriodo.reduce((s, d) => s + d.clientes_con_cpc, 0);
                const gestiones = datosPeriodo.reduce((s, d) => s + d.gestiones_totales, 0);
                const propuestas = datosPeriodo.reduce((s, d) => s + d.monto_propuestas, 0);
                const originaron = datosPeriodo.reduce((s, d) => s + d.usuarios_originaron, 0);
                const origVTA = datosPeriodo.reduce((s, d) => s + d.usuarios_originaron_vta, 0);
                const montoTotal = datosPeriodo.reduce((s, d) => s + d.monto_originado_total, 0);
                const montoCPC = datosPeriodo.reduce((s, d) => s + d.monto_originado_con_cpc, 0);
                const montoVTA = datosPeriodo.reduce((s, d) => s + d.monto_originado_vta, 0);

                const cobertura = base > 0 ? (gestionados * 100 / base).toFixed(2) : 0;
                const pctCPC = base > 0 ? (cpc * 100 / base).toFixed(2) : 0;
                const gestPorUsuario = base > 0 ? (gestiones / base).toFixed(2) : 0;
                const pctOriginadosTotal = base > 0 ? (originaron * 100 / base).toFixed(2) : 0;
                const pctOriginacion = propuestas > 0 ? (montoTotal * 100 / propuestas).toFixed(2) : 0;
                const pctMontoCPC = propuestas > 0 ? (montoCPC * 100 / propuestas).toFixed(2) : 0;
                const pctMontoAtribVTA = montoTotal > 0 ? (montoVTA * 100 / montoTotal).toFixed(2) : 0;
                const pctCltOrigVTATotal = originaron > 0 ? (origVTA * 100 / originaron).toFixed(2) : 0;

                const periodoLabel = periodosDisponibles.find(p => p.value === periodo)?.label || '';
                const esSeleccionado = periodo === periodoSeleccionado ? 'selected' : '';

                html += `
                    <tr class="${{esSeleccionado}}">
                        <td class="periodo-col">${{periodoLabel}}</td>
                        <td class="numero">${{base.toLocaleString()}}</td>
                        <td class="porcentaje">${{cobertura}}%</td>
                        <td class="porcentaje">${{pctCPC}}%</td>
                        <td class="numero">${{gestPorUsuario}}</td>
                        <td class="porcentaje">${{pctOriginadosTotal}}%</td>
                        <td class="porcentaje">${{pctOriginacion}}%</td>
                        <td class="porcentaje">${{pctMontoCPC}}%</td>
                        <td class="porcentaje">${{pctMontoAtribVTA}}%</td>
                        <td class="porcentaje">${{pctCltOrigVTATotal}}%</td>
                    </tr>
                `;
            }});

            document.getElementById('tablaBody').innerHTML = html;
        }}

        function actualizarTablaPorCriterio() {{
            // Obtener el criterio seleccionado del radio button
            const radioSeleccionado = document.querySelector('input[name="criterioTabla"]:checked');
            if (!radioSeleccionado) {{
                document.getElementById('tablaCriterioBody').innerHTML = '<tr><td colspan="10" style="text-align: center;">Selecciona un criterio</td></tr>';
                return;
            }}
            const criterioSeleccionado = radioSeleccionado.value;

            // Actualizar clase selected visualmente
            document.querySelectorAll('#criterioListaTabla .criterio-item').forEach(item => {{
                const radio = item.querySelector('input[type="radio"]');
                if (radio && radio.checked) {{
                    item.classList.add('selected');
                }} else {{
                    item.classList.remove('selected');
                }}
            }});

            // Aplicar solo filtros de Producto y Segmento (NO el filtro de criterios múltiple)
            const producto = document.getElementById('filtroProducto').value;
            const segmento = document.getElementById('filtroSegmento').value;

            const datos = datosCompletos.filter(d => {{
                // Aplicar filtros generales
                if (producto !== 'TODOS' && d.tipo_producto !== producto) return false;
                if (segmento !== 'TODOS' && d.tipo_segmento !== segmento) return false;

                // Filtrar por el criterio específico seleccionado
                if (d.criterio !== criterioSeleccionado) return false;

                return true;
            }});

            if (datos.length === 0) {{
                document.getElementById('tablaCriterioBody').innerHTML = '<tr><td colspan="10" style="text-align: center;">No hay datos para este criterio</td></tr>';
                return;
            }}

            const periodosOrdenados = [...new Set(datos.map(d => d.periodo))].sort((a, b) => b - a);

            let html = '';
            periodosOrdenados.forEach(periodo => {{
                const datosPeriodo = datos.filter(d => d.periodo === periodo);

                const base = datosPeriodo.reduce((s, d) => s + d.clientes_asignados, 0);
                const gestionados = datosPeriodo.reduce((s, d) => s + d.clientes_con_gestion, 0);
                const cpc = datosPeriodo.reduce((s, d) => s + d.clientes_con_cpc, 0);
                const gestiones = datosPeriodo.reduce((s, d) => s + d.gestiones_totales, 0);
                const propuestas = datosPeriodo.reduce((s, d) => s + d.monto_propuestas, 0);
                const originaron = datosPeriodo.reduce((s, d) => s + d.usuarios_originaron, 0);
                const origVTA = datosPeriodo.reduce((s, d) => s + d.usuarios_originaron_vta, 0);
                const montoTotal = datosPeriodo.reduce((s, d) => s + d.monto_originado_total, 0);
                const montoCPC = datosPeriodo.reduce((s, d) => s + d.monto_originado_con_cpc, 0);
                const montoVTA = datosPeriodo.reduce((s, d) => s + d.monto_originado_vta, 0);

                const cobertura = base > 0 ? (gestionados * 100 / base).toFixed(2) : 0;
                const pctCPC = base > 0 ? (cpc * 100 / base).toFixed(2) : 0;
                const gestPorUsuario = base > 0 ? (gestiones / base).toFixed(2) : 0;
                const pctOriginadosTotal = base > 0 ? (originaron * 100 / base).toFixed(2) : 0;
                const pctOriginacion = propuestas > 0 ? (montoTotal * 100 / propuestas).toFixed(2) : 0;
                const pctMontoCPC = propuestas > 0 ? (montoCPC * 100 / propuestas).toFixed(2) : 0;
                const pctMontoAtribVTA = montoTotal > 0 ? (montoVTA * 100 / montoTotal).toFixed(2) : 0;
                const pctCltOrigVTATotal = originaron > 0 ? (origVTA * 100 / originaron).toFixed(2) : 0;

                const periodoLabel = periodosDisponibles.find(p => p.value === periodo)?.label || '';
                const esSeleccionado = periodo === periodoSeleccionado ? 'selected' : '';

                html += `
                    <tr class="${{esSeleccionado}}">
                        <td class="periodo-col">${{periodoLabel}}</td>
                        <td class="numero">${{base.toLocaleString()}}</td>
                        <td class="porcentaje">${{cobertura}}%</td>
                        <td class="porcentaje">${{pctCPC}}%</td>
                        <td class="numero">${{gestPorUsuario}}</td>
                        <td class="porcentaje">${{pctOriginadosTotal}}%</td>
                        <td class="porcentaje">${{pctOriginacion}}%</td>
                        <td class="porcentaje">${{pctMontoCPC}}%</td>
                        <td class="porcentaje">${{pctMontoAtribVTA}}%</td>
                        <td class="porcentaje">${{pctCltOrigVTATotal}}%</td>
                    </tr>
                `;
            }});

            document.getElementById('tablaCriterioBody').innerHTML = html;
        }}

        function actualizarTablaVoiceBot() {{
            const datos = filtrarDatos();

            // Obtener los últimos 4 períodos
            const periodosOrdenados = [...new Set(datos.map(d => d.periodo))].sort((a, b) => b - a).slice(0, 4);

            // Actualizar headers
            periodosOrdenados.forEach((periodo, index) => {{
                const label = periodosDisponibles.find(p => p.value === periodo)?.label || '';
                const colHeader = document.getElementById(`vb-col-${{index + 1}}`);
                if (colHeader) colHeader.textContent = label;
            }});

            // Calcular totales por período
            const totalesPorPeriodo = periodosOrdenados.map(periodo => {{
                const datosPeriodo = datos.filter(d => d.periodo === periodo);
                return {{
                    optInVB: datosPeriodo.reduce((s, d) => s + d.clientes_opt_in_vb, 0),
                    telPostOptIn: datosPeriodo.reduce((s, d) => s + d.clientes_tel_post_opt_in, 0),
                    originadosTel: datosPeriodo.reduce((s, d) => s + d.clientes_originados_tel_post_opt_in, 0),
                    montoOriginados: datosPeriodo.reduce((s, d) => s + d.monto_originados_tel_post_opt_in, 0),
                    montoPropuesta: datosPeriodo.reduce((s, d) => s + d.monto_propuesta_tel_post_opt_in, 0),
                    montoTotalOriginado: datosPeriodo.reduce((s, d) => s + d.monto_originado_total, 0),
                    clientesTotalOriginados: datosPeriodo.reduce((s, d) => s + d.usuarios_originaron, 0)
                }};
            }});

            // Construir filas
            let html = '';

            // Fila 1: CTES_UNICOS_CON_OPT_IN_VB
            html += '<tr><td><strong>SUM de CTES_UNICOS_CON_OPT_IN_VB</strong></td>';
            totalesPorPeriodo.forEach(t => {{
                html += `<td class="numero">${{t.optInVB.toLocaleString()}}</td>`;
            }});
            html += '</tr>';

            // Fila 2: CTES_UNICOS_CON_TEL_POST_OPT_IN
            html += '<tr><td><strong>SUM de CTES_UNICOS_CON_TEL_POST_OPT_IN</strong></td>';
            totalesPorPeriodo.forEach(t => {{
                html += `<td class="numero">${{t.telPostOptIn.toLocaleString()}}</td>`;
            }});
            html += '</tr>';

            // Fila 3: CTES_UNICOS_ORIGINADOS_CON_TEL_POST_OPT_IN
            html += '<tr><td><strong>SUM de CTES_UNICOS_ORIGINADOS_CON_TEL_POST_OPT_IN</strong></td>';
            totalesPorPeriodo.forEach(t => {{
                html += `<td class="numero">${{t.originadosTel.toLocaleString()}}</td>`;
            }});
            html += '</tr>';

            // Fila 4: MONTO_ORIGINADOS_CON_TEL_POST_OPT_IN
            html += '<tr><td><strong>SUM de MONTO_ORIGINADOS_CON_TEL_POST_OPT_IN</strong></td>';
            totalesPorPeriodo.forEach(t => {{
                html += `<td class="numero">${{t.montoOriginados.toLocaleString('es-AR', {{minimumFractionDigits: 0, maximumFractionDigits: 0}})}}</td>`;
            }});
            html += '</tr>';

            // Fila 5: MONTO_PROPUESTA_CON_TEL_POST_OPT_IN
            html += '<tr><td><strong>SUM de MONTO_PROPUESTA_CON_TEL_POST_OPT_IN</strong></td>';
            totalesPorPeriodo.forEach(t => {{
                html += `<td class="numero">${{t.montoPropuesta.toLocaleString('es-AR', {{minimumFractionDigits: 0, maximumFractionDigits: 0}})}}</td>`;
            }});
            html += '</tr>';

            // Separador
            html += '<tr style="height: 10px;"><td colspan="5"></td></tr>';

            // KPI 1: COBERTURA VB
            html += '<tr style="background: #E3F2FD;"><td><strong>COBERTURA VB</strong></td>';
            totalesPorPeriodo.forEach(t => {{
                const coberturaVB = t.optInVB > 0 ? (t.telPostOptIn * 100 / t.optInVB).toFixed(2) : 0;
                html += `<td class="porcentaje">${{coberturaVB}}%</td>`;
            }});
            html += '</tr>';

            // KPI 2: CLIENTES ÚNICOS ORIGINADOS TEL/VB
            html += '<tr style="background: #E8F5E9;"><td><strong>CLIENTES ÚNICOS ORIGINADOS TEL/VB</strong></td>';
            totalesPorPeriodo.forEach(t => {{
                const origTelVB = t.telPostOptIn > 0 ? (t.originadosTel * 100 / t.telPostOptIn).toFixed(2) : 0;
                html += `<td class="porcentaje">${{origTelVB}}%</td>`;
            }});
            html += '</tr>';

            // KPI 3: MONTO ORIGINADO TEL/VB
            html += '<tr style="background: #FFF3E0;"><td><strong>MONTO ORIGINADO TEL/VB</strong></td>';
            totalesPorPeriodo.forEach(t => {{
                const montoOrigTelVB = t.montoPropuesta > 0 ? (t.montoOriginados * 100 / t.montoPropuesta).toFixed(2) : 0;
                html += `<td class="porcentaje">${{montoOrigTelVB}}%</td>`;
            }});
            html += '</tr>';

            // KPI 4: MONTO ORIGINADO VB/TOTAL
            html += '<tr style="background: #F3E5F5;"><td><strong>MONTO ORIGINADO VB/TOTAL</strong></td>';
            totalesPorPeriodo.forEach(t => {{
                const montoVBTotal = t.montoTotalOriginado > 0 ? (t.montoOriginados * 100 / t.montoTotalOriginado).toFixed(2) : 0;
                html += `<td class="porcentaje">${{montoVBTotal}}%</td>`;
            }});
            html += '</tr>';

            // KPI 5: CLIENTES ÚNICOS ORIGINADOS VB/TOTAL
            html += '<tr style="background: #E1F5FE;"><td><strong>CLIENTES ÚNICOS ORIGINADOS VB/TOTAL</strong></td>';
            totalesPorPeriodo.forEach(t => {{
                const clientesVBTotal = t.clientesTotalOriginados > 0 ? (t.originadosTel * 100 / t.clientesTotalOriginados).toFixed(2) : 0;
                html += `<td class="porcentaje">${{clientesVBTotal}}%</td>`;
            }});
            html += '</tr>';

            document.getElementById('tablaVBBody').innerHTML = html;
        }}

        function actualizarGraficoCoberturas() {{
            const datos = filtrarDatos();

            // Agrupar por periodo y calcular coberturas
            const datosPorPeriodo = {{}};
            datos.forEach(d => {{
                if (!datosPorPeriodo[d.periodo]) {{
                    datosPorPeriodo[d.periodo] = {{ base: 0, gestionados: 0, cpc: 0 }};
                }}
                datosPorPeriodo[d.periodo].base += d.clientes_asignados;
                datosPorPeriodo[d.periodo].gestionados += d.clientes_con_gestion;
                datosPorPeriodo[d.periodo].cpc += d.clientes_con_cpc;
            }});

            // Tomar solo los últimos 6 meses
            const periodos = Object.keys(datosPorPeriodo).sort().slice(-6);
            const labels = periodos.map(p => {{
                const label = periodosDisponibles.find(x => x.value === parseInt(p))?.label || p;
                return label;
            }});

            const coberturaTotal = periodos.map(p => {{
                const datos = datosPorPeriodo[p];
                return datos.base > 0 ? (datos.gestionados * 100 / datos.base).toFixed(2) : 0;
            }});

            const coberturaCPC = periodos.map(p => {{
                const datos = datosPorPeriodo[p];
                return datos.base > 0 ? (datos.cpc * 100 / datos.base).toFixed(2) : 0;
            }});

            if (chartCoberturas) {{
                chartCoberturas.destroy();
            }}

            const ctx = document.getElementById('chartCoberturas').getContext('2d');
            chartCoberturas = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: labels,
                    datasets: [
                        {{
                            label: 'Cobertura Total (%)',
                            data: coberturaTotal,
                            borderColor: '#00A650',
                            backgroundColor: 'rgba(0, 166, 80, 0.1)',
                            tension: 0.4,
                            fill: true,
                            pointRadius: 6,
                            pointHoverRadius: 8
                        }},
                        {{
                            label: 'Cobertura CPC (%)',
                            data: coberturaCPC,
                            borderColor: '#009EE3',
                            backgroundColor: 'rgba(0, 158, 227, 0.1)',
                            tension: 0.4,
                            fill: true,
                            pointRadius: 6,
                            pointHoverRadius: 8
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            display: true,
                            position: 'top'
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    return context.dataset.label + ': ' + context.parsed.y.toFixed(2) + '%';
                                }}
                            }}
                        }}
                    }},
                    layout: {{
                        padding: {{
                            top: 30
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            ticks: {{
                                callback: function(value) {{
                                    return value + '%';
                                }}
                            }}
                        }}
                    }}
                }},
                plugins: [{{
                    afterDatasetsDraw: function(chart) {{
                        const ctx = chart.ctx;
                        chart.data.datasets.forEach((dataset, i) => {{
                            const meta = chart.getDatasetMeta(i);
                            if (!meta.hidden) {{
                                meta.data.forEach((element, index) => {{
                                    ctx.fillStyle = dataset.borderColor;
                                    ctx.font = 'bold 11px Arial';
                                    ctx.textAlign = 'center';
                                    ctx.textBaseline = 'bottom';
                                    const data = dataset.data[index];
                                    ctx.fillText(data + '%', element.x, element.y - 8);
                                }});
                            }}
                        }});
                    }}
                }}]
            }});
        }}

        function actualizarGraficoMontoAtribuido() {{
            const datos = filtrarDatos();

            // Agrupar por periodo
            const datosPorPeriodo = {{}};
            datos.forEach(d => {{
                if (!datosPorPeriodo[d.periodo]) {{
                    datosPorPeriodo[d.periodo] = {{ montoVTA: 0, montoTotal: 0 }};
                }}
                datosPorPeriodo[d.periodo].montoVTA += d.monto_originado_vta;
                datosPorPeriodo[d.periodo].montoTotal += d.monto_originado_total;
            }});

            const periodos = Object.keys(datosPorPeriodo).sort();
            const labels = periodos.map(p => {{
                const label = periodosDisponibles.find(x => x.value === parseInt(p))?.label || p;
                return label;
            }});

            const valores = periodos.map(p => {{
                const datos = datosPorPeriodo[p];
                return datos.montoTotal > 0 ? (datos.montoVTA * 100 / datos.montoTotal).toFixed(2) : 0;
            }});

            if (chartMontoAtribuido) {{
                chartMontoAtribuido.destroy();
            }}

            const ctx = document.getElementById('chartMontoAtribuido').getContext('2d');
            chartMontoAtribuido = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: labels,
                    datasets: [{{
                        label: 'Monto Atribuido VTA (%)',
                        data: valores,
                        borderColor: '#FF7A00',
                        backgroundColor: 'rgba(255, 122, 0, 0.1)',
                        tension: 0.4,
                        fill: true,
                        pointRadius: 6,
                        pointHoverRadius: 8
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            display: true,
                            position: 'top'
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    return context.dataset.label + ': ' + context.parsed.y.toFixed(2) + '%';
                                }}
                            }}
                        }}
                    }},
                    layout: {{
                        padding: {{
                            top: 30
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            ticks: {{
                                callback: function(value) {{
                                    return value + '%';
                                }}
                            }}
                        }}
                    }}
                }},
                plugins: [{{
                    afterDatasetsDraw: function(chart) {{
                        const ctx = chart.ctx;
                        chart.data.datasets.forEach((dataset, i) => {{
                            const meta = chart.getDatasetMeta(i);
                            if (!meta.hidden) {{
                                meta.data.forEach((element, index) => {{
                                    ctx.fillStyle = dataset.borderColor;
                                    ctx.font = 'bold 11px Arial';
                                    ctx.textAlign = 'center';
                                    ctx.textBaseline = 'bottom';
                                    const data = dataset.data[index];
                                    ctx.fillText(data + '%', element.x, element.y - 8);
                                }});
                            }}
                        }});
                    }}
                }}]
            }});
        }}

        function actualizarGraficoTicketPromedio() {{
            const datos = filtrarDatos();

            // Agrupar por periodo
            const datosPorPeriodo = {{}};
            datos.forEach(d => {{
                if (!datosPorPeriodo[d.periodo]) {{
                    datosPorPeriodo[d.periodo] = {{
                        montoTotal: 0,
                        usuariosTotal: 0,
                        montoVTA: 0,
                        montoTotalVTA: 0,
                        usuariosVTA: 0
                    }};
                }}
                datosPorPeriodo[d.periodo].montoTotal += d.monto_originado_total;
                datosPorPeriodo[d.periodo].usuariosTotal += d.usuarios_originaron;
                datosPorPeriodo[d.periodo].montoVTA += d.monto_originado_vta;
                datosPorPeriodo[d.periodo].montoTotalVTA += d.monto_total_vta;
                datosPorPeriodo[d.periodo].usuariosVTA += d.usuarios_originaron_vta;
            }});

            const periodos = Object.keys(datosPorPeriodo).sort();
            const labels = periodos.map(p => {{
                const label = periodosDisponibles.find(x => x.value === parseInt(p))?.label || p;
                return label;
            }});

            const ticketPromedioTotal = periodos.map(p => {{
                const datos = datosPorPeriodo[p];
                return datos.usuariosTotal > 0 ? (datos.montoTotal / datos.usuariosTotal).toFixed(2) : 0;
            }});

            const ticketPromedioVTA = periodos.map(p => {{
                const datos = datosPorPeriodo[p];
                return datos.usuariosVTA > 0 ? (datos.montoVTA / datos.usuariosVTA).toFixed(2) : 0;
            }});

            const ticketPromedioAtribucionVTA = periodos.map(p => {{
                const datos = datosPorPeriodo[p];
                return datos.usuariosVTA > 0 ? (datos.montoTotalVTA / datos.usuariosVTA).toFixed(2) : 0;
            }});

            if (chartTicketPromedio) {{
                chartTicketPromedio.destroy();
            }}

            const ctx = document.getElementById('chartTicketPromedio').getContext('2d');
            chartTicketPromedio = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: labels,
                    datasets: [
                        {{
                            label: 'Ticket Promedio Total',
                            data: ticketPromedioTotal,
                            borderColor: '#2196F3',
                            backgroundColor: 'rgba(33, 150, 243, 0.08)',
                            tension: 0.4,
                            fill: true,
                            pointRadius: 7,
                            pointHoverRadius: 10,
                            pointBackgroundColor: '#2196F3',
                            pointBorderColor: '#fff',
                            pointBorderWidth: 3,
                            pointHoverBackgroundColor: '#2196F3',
                            pointHoverBorderColor: '#fff',
                            borderWidth: 3,
                            order: 1
                        }},
                        {{
                            label: 'Ticket Promedio VTA (Usuario)',
                            data: ticketPromedioVTA,
                            borderColor: '#FF7A00',
                            backgroundColor: 'rgba(255, 122, 0, 0.08)',
                            tension: 0.4,
                            fill: true,
                            pointRadius: 7,
                            pointHoverRadius: 10,
                            pointBackgroundColor: '#FF7A00',
                            pointBorderColor: '#fff',
                            pointBorderWidth: 3,
                            pointHoverBackgroundColor: '#FF7A00',
                            pointHoverBorderColor: '#fff',
                            borderWidth: 3,
                            order: 2
                        }},
                        {{
                            label: 'Ticket Promedio Atribución VTA',
                            data: ticketPromedioAtribucionVTA,
                            borderColor: '#4CAF50',
                            backgroundColor: 'rgba(76, 175, 80, 0.08)',
                            tension: 0.4,
                            fill: true,
                            pointRadius: 7,
                            pointHoverRadius: 10,
                            pointBackgroundColor: '#4CAF50',
                            pointBorderColor: '#fff',
                            pointBorderWidth: 3,
                            pointHoverBackgroundColor: '#4CAF50',
                            pointHoverBorderColor: '#fff',
                            borderWidth: 3,
                            order: 3
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {{
                        mode: 'index',
                        intersect: false
                    }},
                    plugins: {{
                        legend: {{
                            display: true,
                            position: 'top',
                            labels: {{
                                font: {{
                                    size: 13,
                                    weight: 'bold',
                                    family: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
                                }},
                                padding: 20,
                                usePointStyle: true,
                                pointStyle: 'circle',
                                boxWidth: 8,
                                boxHeight: 8
                            }}
                        }},
                        tooltip: {{
                            enabled: true,
                            backgroundColor: 'rgba(0, 0, 0, 0.85)',
                            titleColor: '#fff',
                            bodyColor: '#fff',
                            borderColor: '#ddd',
                            borderWidth: 1,
                            padding: 15,
                            displayColors: true,
                            titleFont: {{
                                size: 14,
                                weight: 'bold'
                            }},
                            bodyFont: {{
                                size: 13
                            }},
                            callbacks: {{
                                label: function(context) {{
                                    const value = parseFloat(context.parsed.y).toLocaleString('es-AR', {{
                                        minimumFractionDigits: 0,
                                        maximumFractionDigits: 0
                                    }});
                                    return ' ' + context.dataset.label + ': $' + value;
                                }}
                            }}
                        }}
                    }},
                    layout: {{
                        padding: {{
                            top: 35,
                            bottom: 10
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            grid: {{
                                color: 'rgba(0, 0, 0, 0.05)',
                                drawBorder: false
                            }},
                            ticks: {{
                                callback: function(value) {{
                                    return '$' + (value / 1000).toFixed(0) + 'K';
                                }},
                                font: {{
                                    size: 12,
                                    family: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
                                }},
                                color: '#666',
                                padding: 8
                            }}
                        }},
                        x: {{
                            grid: {{
                                color: 'rgba(0, 0, 0, 0.03)',
                                drawBorder: false
                            }},
                            ticks: {{
                                font: {{
                                    size: 12,
                                    weight: '600',
                                    family: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
                                }},
                                color: '#555',
                                padding: 8
                            }}
                        }}
                    }}
                }},
                plugins: [{{
                    afterDatasetsDraw: function(chart) {{
                        const ctx = chart.ctx;
                        chart.data.datasets.forEach((dataset, i) => {{
                            const meta = chart.getDatasetMeta(i);
                            if (!meta.hidden) {{
                                meta.data.forEach((element, index) => {{
                                    const data = dataset.data[index];
                                    if (data && data > 0) {{
                                        // Fondo blanco para el texto
                                        ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
                                        ctx.strokeStyle = dataset.borderColor;
                                        ctx.lineWidth = 2;

                                        const formattedValue = (parseFloat(data) / 1000).toFixed(0) + 'K';
                                        const text = '$' + formattedValue;

                                        ctx.font = 'bold 11px "Segoe UI", Arial, sans-serif';
                                        const textWidth = ctx.measureText(text).width;
                                        const padding = 6;

                                        const boxX = element.x - (textWidth / 2) - padding;
                                        const boxY = element.y - 28;
                                        const boxWidth = textWidth + (padding * 2);
                                        const boxHeight = 18;

                                        // Dibujar fondo redondeado
                                        ctx.beginPath();
                                        ctx.roundRect(boxX, boxY, boxWidth, boxHeight, 4);
                                        ctx.fill();
                                        ctx.stroke();

                                        // Dibujar texto
                                        ctx.fillStyle = dataset.borderColor;
                                        ctx.textAlign = 'center';
                                        ctx.textBaseline = 'middle';
                                        ctx.fillText(text, element.x, element.y - 19);
                                    }}
                                }});
                            }}
                        }});
                    }}
                }}]
            }});
        }}

        inicializarFiltros();
        actualizarKPIs();
        actualizarTablaComparativa();
        actualizarTablaPorCriterio();
        actualizarTablaVoiceBot();
        actualizarGraficoCoberturas();
        actualizarGraficoMontoAtribuido();
        actualizarGraficoTicketPromedio();
    </script>
</body>
</html>
"""

with open(archivo_salida, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\nDashboard ZOLVEX generado!")
print(f"Archivo: {archivo_salida}")
print(f"Registros: {len(df)}")
print(f"Periodos disponibles: {len(periodos_disponibles)}")
print("=" * 80)
