# Usamos la versión de Python especificada en tu README
FROM python:3.12

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos el archivo de requerimientos (asegúrate de tener psycopg2-binary y python-dotenv ahí)
COPY requirements.txt .

# Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el código de tu proyecto al contenedor
COPY . .

# Comando por defecto al ejecutar el contenedor (puedes cambiarlo al script que desees probar primero)
CMD ["python", "script/carga_bd.py"]