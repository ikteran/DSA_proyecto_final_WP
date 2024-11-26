FROM python:3.10

# Definir directorio de trabajo 
WORKDIR /opt/waypoint

# Instalar dependencias
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación
COPY . .

# Puerto a exponer para la api 
EXPOSE 8050

# Comando para iniciar la aplicación
CMD ["python3", "app.py"]