"""
Script para actualizar automáticamente el dashboard ZOLVEX y subirlo a GitHub
"""
import subprocess
import sys
from datetime import datetime
import os

# Cambiar al directorio del script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print(f"ACTUALIZACIÓN AUTOMÁTICA DEL DASHBOARD ZOLVEX - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

try:
    # 1. Generar el dashboard actualizado
    print("\n[1/3] Generando dashboard actualizado...")
    result = subprocess.run([sys.executable, "generar_dashboard.py"],
                          capture_output=True, text=True, timeout=300)

    if result.returncode != 0:
        print("ERROR al generar dashboard:")
        print(result.stderr)
        sys.exit(1)

    print(result.stdout)
    print("[OK] Dashboard generado exitosamente")

    # 2. Hacer commit de los cambios
    print("\n[2/3] Haciendo commit de cambios...")

    # Añadir index.html
    subprocess.run(["git", "add", "index.html"], check=True)

    # Commit con mensaje automático
    commit_msg = f"Dashboard actualizado automáticamente - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    subprocess.run(["git", "commit", "-m", commit_msg], check=True)
    print(f"[OK] Commit realizado: {commit_msg}")

    # 3. Push a GitHub
    print("\n[3/3] Subiendo a GitHub...")
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("[OK] Dashboard publicado en GitHub Pages")

    print("\n" + "=" * 80)
    print("[OK] ACTUALIZACION COMPLETADA EXITOSAMENTE")
    print("[OK] Dashboard disponible en: https://sofiarodriguez-png.github.io/dashboard-zolvex/")
    print("=" * 80)

except subprocess.TimeoutExpired:
    print("ERROR: El script tardó demasiado en ejecutarse (timeout)")
    sys.exit(1)
except subprocess.CalledProcessError as e:
    print(f"ERROR en el proceso: {e}")
    sys.exit(1)
except Exception as e:
    print(f"ERROR inesperado: {e}")
    sys.exit(1)
