# 🔬 Experimento 1 — Tamaño de Payload: gRPC/Protobuf vs. REST/JSON

> **Fecha de ejecución:** 2026-09-25 22:36:39
> **Competencia ABET 6** · Integración de Sistemas · Universidad de Concepción

---

## 1. Objetivo

Comparar la eficiencia en consumo de ancho de banda entre la serialización
binaria de Protocol Buffers (gRPC) y la serialización en texto JSON (REST),
incluyendo el efecto de la compresión gzip sobre ambos formatos.

## 2. Hipótesis

> *"El formato binario de Protocol Buffers reduce el tamaño del payload en al
> menos un 50% en comparación con JSON sin comprimir, aunque esta brecha se
> estrecha al aplicar compresión gzip a JSON."*

## 3. Diseño Experimental

### Variables
- **Variable Independiente**: Cantidad de sectores serializados (1, 5, 10, 25, 50, 100) y formato de serialización (JSON, JSON+gzip, Protobuf, Protobuf+gzip).
- **Variable Dependiente**: Tamaño del payload en bytes.

### Variables Controladas
- Estructura de datos idéntica en ambos formatos (mismos campos, mismos valores).
- Mismo contenido textual para los nombres de sector.
- Compresión gzip con nivel por defecto (9) en ambos casos.
- Entorno de ejecución: Python 3.14.7, protobuf proto3.

### Método
1. Para cada escala N ∈ {1, 5, 10, 25, 50, 100}:
   - Se generan N sectores con datos simulados de estructura fija.
   - Se serializan con `json.dumps()` (UTF-8) → se mide `len()` en bytes.
   - Se aplica `gzip.compress()` al JSON → se mide el tamaño comprimido.
   - Se serializan con `protobuf.SerializeToString()` → se mide `len()`.
   - Se aplica `gzip.compress()` al payload protobuf → se mide el tamaño.
2. Cada medición se repite **10 veces** para verificar determinismo.
3. Los resultados se registran en CSV y se resumen en tabla promediada.

## 4. Resultados

### 4.1 Tabla de Resultados (promedio de 10 repeticiones)

| Cant. Sectores | JSON (bytes) | JSON+gzip (bytes) | Protobuf (bytes) | Protobuf+gzip (bytes) | Ahorro PB vs JSON | Ahorro PB+gz vs JSON+gz |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | 113 | 110 | 46 | 66 | 59.3% | 40.0% |
| 5 | 565 | 156 | 230 | 106 | 59.3% | 32.0% |
| 10 | 1,130 | 193 | 460 | 145 | 59.3% | 24.9% |
| 25 | 2,870 | 316 | 1,195 | 261 | 58.4% | 17.4% |
| 50 | 5,770 | 507 | 2,420 | 417 | 58.1% | 17.8% |
| 100 | 11,570 | 901 | 4,870 | 734 | 57.9% | 18.5% |

### 4.2 Observaciones de los Datos

- **Ahorro promedio de Protobuf vs JSON sin comprimir:** 58.7% (rango: 57.9% – 59.3%).
- **Ahorro promedio de Protobuf+gzip vs JSON+gzip:** 25.1%.
- Las mediciones son **deterministas** (10 repeticiones idénticas por escala), lo que confirma que no hay variabilidad aleatoria en la serialización.
- Con pocos elementos (N=1), el overhead de las claves JSON es proporcionalmente alto, maximizando la ventaja de Protobuf.
- A medida que N crece, el ahorro relativo tiende a estabilizarse porque la estructura repetitiva se vuelve dominante.

## 5. Análisis y Conclusiones

### 5.1 Sobre la hipótesis

✅ **Hipótesis confirmada.** El ahorro promedio de Protobuf frente a JSON es de **58.7%**, superando el umbral del 50% planteado.

### 5.2 Efecto de la compresión gzip

La brecha **se estrecha significativamente** al aplicar compresión:
- Sin compresión: Protobuf ahorra ~59% respecto a JSON.
- Con compresión: la ventaja de Protobuf baja a ~25%.

Esto se explica porque **gzip comprime muy bien las estructuras repetitivas de JSON** (claves duplicadas como `"sector_id"`, `"nombre"`, etc.), reduciendo gran parte de la redundancia que Protobuf evita por diseño (usa números de campo en lugar de claves texto).

### 5.3 Matices y limitaciones

1. **La compresión no es gratuita**: gzip añade consumo de CPU. En un entorno de alto volumen, el costo de comprimir cada mensaje JSON puede ser relevante, mientras que Protobuf es ligero sin necesitar compresión adicional.
2. **Estos datos miden solo el tamaño del payload**, no incluyen los headers HTTP/1.1 (REST) ni los frames HTTP/2 (gRPC). En la práctica, REST añade varios cientos de bytes en headers por petición.
3. **El contenido textual de los campos influye**: si los nombres de sector fueran más largos, JSON crecería más rápido que Protobuf porque este último codifica strings con solo un byte de prefijo de longitud.
4. **Protobuf omite campos con valor por defecto** (ej: `plazas_libres = 0` no se serializa), lo cual en un estacionamiento lleno reduciría aún más el payload.
5. **El experimento se ejecutó en un solo entorno**; sin embargo, la serialización es determinista y los resultados serían idénticos en cualquier plataforma.

### 5.4 Juicio de ingeniería

Los resultados respaldan la decisión arquitectónica del **ADR-002** (REST hacia afuera, gRPC hacia adentro):
- Para la **API pública** (REST), la universalidad y facilidad de depuración de JSON justifican su mayor tamaño, especialmente si se habilita compresión gzip a nivel de servidor HTTP.
- Para la **comunicación interna** de alto volumen (Accesos → Sensores), Protobuf es la opción más eficiente: payload compacto sin necesidad de compresión adicional, y con un contrato tipado que previene errores.

## 6. Reproducibilidad

Para reproducir este experimento:

```bash
cd G11_INTEGRACION
# Compilar proto (si no existe sensores_pb2.py en docs/experimentos/)
.venv/bin/python3 -m grpc_tools.protoc -I./proto \
    --python_out=./docs/experimentos \
    --grpc_python_out=./docs/experimentos \
    ./proto/sensores.proto

# Ejecutar el experimento
.venv/bin/python3 docs/experimentos/experimento1_payload.py
```

Los datos crudos están disponibles en [`resultados_experimento1.csv`](./resultados_experimento1.csv).
