FROM python:3.10-slim

WORKDIR /app

COPY sensores/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY proto/sensores.proto ./proto/
RUN python -m grpc_tools.protoc -I./proto --python_out=. --grpc_python_out=. ./proto/sensores.proto

COPY sensores/main.py .

EXPOSE 50051

CMD ["python", "main.py"]