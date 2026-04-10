"""
Script de prueba para verificar la conexion a BigQuery y los datos de ZOLVEX
"""
import sys
sys.path.append(r'C:\Users\sorodriguez\CodigosPy')
from bigquery_connection import conectar_bigquery

print("=" * 80)
print("TEST DE CONEXION - DASHBOARD ZOLVEX")
print("=" * 80)

try:
    print("\n[1/3] Conectando a BigQuery...")
    cliente = conectar_bigquery()
    print("[OK] Conexion establecida")

    print("\n[2/3] Consultando datos de ZOLVEX...")
    query = """
    SELECT
        COUNT(*) as total_registros,
        COUNT(DISTINCT COL_MONTH_ID) as periodos,
        COUNT(DISTINCT COL_ASSIGNED_CRITERIA_DESC) as criterios,
        MAX(COL_MONTH_ID) as ultimo_periodo
    FROM `meli-bi-data.SBOX_COLLECTIONSDA.TLV_CONSUMER_BASE_KPIS_FINAL`
    WHERE
        SIT_SITE_ID = 'MLA'
        AND COL_LAST_CALL_CENTER_ASSIGNED = 'ZOLVEX'
        AND LISTA_GESTION = 1
        AND COL_MONTH_ID >= CAST(FORMAT_DATE('%Y%m', DATE_SUB(CURRENT_DATE(), INTERVAL 6 MONTH)) AS INT64)
    """

    df = cliente.query(query).to_dataframe()

    if df.empty:
        print("[ERROR] No se encontraron datos!")
        sys.exit(1)

    print("[OK] Datos encontrados")

    print("\n[3/3] Resumen de datos:")
    print(f"  - Total de registros: {df['total_registros'].iloc[0]:,}")
    print(f"  - Periodos disponibles: {df['periodos'].iloc[0]}")
    print(f"  - Criterios unicos: {df['criterios'].iloc[0]}")
    print(f"  - Ultimo periodo: {df['ultimo_periodo'].iloc[0]}")

    print("\n" + "=" * 80)
    print("[OK] TEST EXITOSO - El dashboard puede generarse correctamente")
    print("=" * 80)

except Exception as e:
    print(f"\n[ERROR] {str(e)}")
    print("\nVerifica:")
    print("  1. Conexion a internet")
    print("  2. Credenciales de BigQuery")
    print("  3. Permisos en la tabla")
    sys.exit(1)
