"""
main.py -- Punto de Entrada Único del Proyecto
================================================
Ejecuta todo el pipeline del proyecto en orden con un solo comando:

    python main.py

Pasos que se ejecutan:
    1. Monitoreo y control de calidad de datos (monitoreo_alertas.py)
    2. Limpieza y transformacion de datos (clean.py)
    3. Entrenamiento del modelo (train_model.py)
    4. Evaluacion y metricas del modelo (test_model.py)
"""

import subprocess
import sys
import os

# Directorio raiz del proyecto (donde esta este archivo)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_DIR = os.path.join(ROOT_DIR, "script")

SEP = "=" * 55


def ejecutar_paso(nombre, script):
    """Ejecuta un script de Python y detiene el pipeline si falla."""
    print(f"\n{SEP}")
    print(f"  PASO: {nombre}")
    print(SEP)

    resultado = subprocess.run(
        [sys.executable, script],
        cwd=ROOT_DIR
    )

    if resultado.returncode != 0:
        print(f"\n[ERROR] El paso '{nombre}' falló con código {resultado.returncode}.")
        print("[PIPELINE] Ejecución detenida.")
        sys.exit(resultado.returncode)

    print(f"[OK] '{nombre}' completado exitosamente.")


if __name__ == "__main__":
    print(f"\n{SEP}")
    print("  PIPELINE COMPLETO -- Loan Approval Project")
    print(SEP)

    pasos = [
        ("1. Monitoreo y Calidad de Datos", os.path.join(SCRIPT_DIR, "monitoreo_alertas.py")),
        ("2. Limpieza y Transformacion",    os.path.join(SCRIPT_DIR, "clean.py")),
        ("3. Entrenamiento del Modelo",     os.path.join(SCRIPT_DIR, "train_model.py")),
        ("4. Evaluacion del Modelo",        os.path.join(SCRIPT_DIR, "test_model.py")),
    ]

    for nombre, script in pasos:
        ejecutar_paso(nombre, script)

    print(f"\n{SEP}")
    print("  PIPELINE FINALIZADO EXITOSAMENTE")
    print(f"{SEP}\n")
