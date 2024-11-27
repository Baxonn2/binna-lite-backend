# Usar la imagen oficial de Python
FROM python:3.12.3

# Crear un directorio de trabajo
WORKDIR /app

# Copiar los archivos de requisitos y la aplicación
COPY requirements.txt .
COPY . .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Crear un volumen para la base de datos
VOLUME /app/db

# Exponer el puerto 8000
EXPOSE 8000

# Comando para correr la aplicación
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
