"""
carga_bd.py — Carga de Datos Limpios en PostgreSQL
===================================================
Importa el pipeline de limpieza (clean.py), obtiene el DataFrame
procesado y lo inserta de forma eficiente en la tabla 'loan_data'
de la base de datos PostgreSQL configurada en el archivo .env.
"""

import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

# Importamos el pipeline de limpieza
from clean import pipeline_limpieza

# Carga las variables del archivo .env automáticamente
load_dotenv()


def obtener_conexion():
    """Crea y devuelve una conexión a PostgreSQL usando las variables de entorno."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


def cargar_datos():
    """
    Orquesta el pipeline completo:
      1. Limpia y transforma los datos con clean.pipeline_limpieza()
      2. Conecta a PostgreSQL
      3. Inserta los registros en lote en la tabla 'loan_data'
    """
    conexion = None
    cursor = None

    try:
        # ── 1. LIMPIEZA Y TRANSFORMACIÓN ──────────────────────────────────────
        df = pipeline_limpieza()

        # ── 2. CONEXIÓN A LA BASE DE DATOS ────────────────────────────────────
        print("[BD] Conectando a PostgreSQL...")
        conexion = obtener_conexion()
        conexion.autocommit = True
        cursor = conexion.cursor()
        print(f"[BD] Conexión establecida con '{os.getenv('DB_NAME')}' en {os.getenv('DB_HOST')}")

        # ── 3. INSERCIÓN EN LOTE (batch insert) ───────────────────────────────
        query_insertar = """
            INSERT INTO loan_data (
                person_age, person_gender, person_education, person_income,
                person_emp_exp, person_home_ownership, loan_amnt, loan_intent,
                loan_int_rate, loan_percent_income, cb_person_cred_hist_length,
                credit_score, previous_loan_defaults_on_file, loan_status
            ) VALUES %s;
        """

        # Convertir el DataFrame a lista de tuplas
        valores = [tuple(fila) for fila in df.to_numpy()]

        # execute_values inserta en bloques de 1 000 filas por batch (mucho más rápido que row-by-row)
        psycopg2.extras.execute_values(cursor, query_insertar, valores, page_size=1_000)

        print(f"[BD] ✓ {len(df):,} registros insertados correctamente en 'loan_data'.")

    except psycopg2.OperationalError as e:
        print(f"[ERROR] No se pudo conectar a PostgreSQL: {e}")
        raise
    except Exception as e:
        print(f"[ERROR] Fallo durante la carga: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()
            print("[BD] Conexión cerrada.")


# ─── Punto de entrada ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    cargar_datos()