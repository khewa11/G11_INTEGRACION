FROM python:3.10-slim

WORKDIR /app

# 1. Copiar e instalar dependencias
COPY accesos/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copiar el contrato gRPC desde la carpeta compartida proto/
COPY proto/sensores.proto ./proto/

# 3. Compilar el proto para generar sensores_pb2.py y sensores_pb2_grpc.py dentro del contenedor
RUN python -m grpc_tools.protoc -I./proto --python_out=. --grpc_python_out=. ./proto/sensores.proto

# 4. Copiar todo el código del microservicio de accesos
COPY accesos/ .

EXPOSE 8000

# 5. Comando para iniciar la API REST con Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]