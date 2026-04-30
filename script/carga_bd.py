import psycopg2
import psycopg2.extras
import pandas as pd
import os
from dotenv import load_dotenv

# Esto carga las variables de tu archivo .env automáticamente
load_dotenv()

def cargar_datos():
    try:
        # Nos conectamos usando las variables de entorno, sin exponer contraseñas
        conexion = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        
        conexion.autocommit = True 
        cursor = conexion.cursor()

        # 1. LEER EL CSV CON PANDAS
        csv_path = os.path.join(os.path.dirname(__file__), "../data/02_loan_data.csv")
        df = pd.read_csv(csv_path)
        print(f"CSV cargado: {len(df)} filas encontradas.")

        # 2. ADAPTAR DATOS A LA BASE DE DATOS
        # Convertir previous_loan_defaults_on_file a booleano
        df['previous_loan_defaults_on_file'] = df['previous_loan_defaults_on_file'].map(
            {'Yes': True, 'No': False, True: True, False: False}
        )
        
        # Convertir loan_status a booleano (0 -> False, 1 -> True)
        df['loan_status'] = df['loan_status'].astype(bool)
        
        # Reemplazar valores NaN por None para que se inserten como NULL en PostgreSQL
        df = df.where(pd.notnull(df), None)

        # 3. INSERTAR DATOS EN LA TABLA loan_data (USANDO execute_values PARA OPTIMIZAR)
        query_insertar = """
        INSERT INTO loan_data 
        (person_age, person_gender, person_education, person_income, person_emp_exp, 
         person_home_ownership, loan_amnt, loan_intent, loan_int_rate, loan_percent_income, 
         cb_person_cred_hist_length, credit_score, previous_loan_defaults_on_file, loan_status) 
        VALUES %s;
        """
        
        # Convertir el DataFrame a una lista de tuplas
        valores = [tuple(x) for x in df.to_numpy()]
        
        # Ejecutar inserción en bloque (batch insert) que es mucho más rápida
        psycopg2.extras.execute_values(cursor, query_insertar, valores, page_size=1000)
        
        print(f"✓ {len(df)} registros insertados correctamente en la tabla 'loan_data'.")

    except Exception as error:
        print(f"Error al conectar con PostgreSQL: {error}")

    finally:
        if 'conexion' in locals() and conexion:
            cursor.close()
            conexion.close()
            print("Conexión cerrada.")

# Ejecutar el script
if __name__ == "__main__":
    cargar_datos()