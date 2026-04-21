import psycopg2
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

        # 1. CREAR LA TABLA (Ajusta las columnas según lo que tenga tu 02_loan_data.csv)
        query_crear_tabla = """
        CREATE TABLE IF NOT EXISTS prestamos (
            id SERIAL PRIMARY KEY,
            monto_prestamo NUMERIC,
            tasa_interes NUMERIC,
            estado_prestamo VARCHAR(50)
            -- Agrega aquí el resto de las columnas de tu CSV
        );
        """
        cursor.execute(query_crear_tabla)
        print("Tabla 'prestamos' lista.")

        # 2. INSERTAR DATOS (Aquí eventualmente leerás tu CSV e insertarás las filas)
        # Por ahora, un ejemplo de prueba:
        query_insertar = """
        INSERT INTO prestamos (monto_prestamo, tasa_interes, estado_prestamo) 
        VALUES (%s, %s, %s);
        """
        valores_prueba = (5000.50, 12.5, "Aprobado")
        
        cursor.execute(query_insertar, valores_prueba)
        print("Datos insertados correctamente en la base de datos.")

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