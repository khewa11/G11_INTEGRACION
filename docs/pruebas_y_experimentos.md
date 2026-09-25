# 🧪 Guía de Pruebas y Experimentos — Proyecto G11 Integración

> **Dominio:** Forma C — Sistema de Gestión de Estacionamiento  
> **Asignatura:** Integración de Sistemas — Universidad de Concepción  

---

## 📋 Parte 1: Batería de Pruebas de Funcionamiento (Requisitos T1 a T7)

Esta batería de pruebas permite verificar que el sistema cumple con todos los requisitos obligatorios antes de la entrega y sirve como guion paso a paso para la grabación del **video demostrativo (máx. 8 minutos)**.

---

### 1.1 Despliegue con Docker (Requisito T1)

Levanta todo el sistema con un solo comando:

```bash
docker compose up --build
```

**Verificación:**
- El contenedor `gRPC_sensores` inicia en el puerto `50051`.
- El contenedor `api_accesos` inicia en el puerto `8000`.
- Ambos contenedores se mantienen en estado *running*.

---

### 1.2 Pruebas de la API REST (Requisitos T2, T4, T5, T6)

> Nota: Las peticiones pueden realizarse mediante `curl`, Postman o desde la interfaz Swagger en `http://localhost:8000/docs`.

#### 🔒 Test 1: Autenticación API Key (Requisito T6)
Probar acceso sin credenciales o con credenciales inválidas:

```bash
# Sin cabecera
curl -i -X GET "http://localhost:8000/v1/vehiculos/"

# Con clave errónea
curl -i -X GET "http://localhost:8000/v1/vehiculos/" \
  -H "X-API-Key: clave_incorrecta"
```
* **Resultado esperado:** Código `403 Forbidden` (`{"detail": "No autorizado"}`).

---

#### 🚗 Test 2: Registro de Vehículos
Registrar un vehículo válido con la API Key correcta (`supersecreto`):

```bash
curl -i -X POST "http://localhost:8000/v1/vehiculos/" \
  -H "X-API-Key: supersecreto" \
  -H "Content-Type: application/json" \
  -d '{"patente": "KKL-88"}'
```
* **Resultado esperado:** HTTP `201 Created` con el JSON del vehículo registrado.

---

#### 📋 Test 3: Listar y Consultar Vehículos

```bash
# Listar todos los vehículos
curl -i -X GET "http://localhost:8000/v1/vehiculos/" \
  -H "X-API-Key: supersecreto"

# Consultar por patente
curl -i -X GET "http://localhost:8000/v1/vehiculos/KKL-88" \
  -H "X-API-Key: supersecreto"
```
* **Resultado esperado:** HTTP `200 OK` con los datos correspondientes.

---

#### 🎟️ Test 4: Emisión de Ticket con Verificación gRPC (Requisito T4)
Emitir ticket en `sec-a` (sector con plazas disponibles):

```bash
curl -i -X POST "http://localhost:8000/v1/tickets/" \
  -H "X-API-Key: supersecreto" \
  -H "Content-Type: application/json" \
  -d '{"patente": "KKL-88", "sector_id": "sec-a"}'
```
* **Resultado esperado:** HTTP `201 Created` con `{"id": 1, "patente": "KKL-88", "sector_id": "sec-a", "estado": "activo"}`.
* **Verificación interna:** Accesos consultó y ocupó exitosamente una plaza en Sensores vía gRPC.

---

#### 🚫 Test 5: Rechazo de Ticket por Sector Lleno (Regla de Negocio)
El sector `sec-b` se inicia con 0 plazas libres:

```bash
curl -i -X POST "http://localhost:8000/v1/tickets/" \
  -H "X-API-Key: supersecreto" \
  -H "Content-Type: application/json" \
  -d '{"patente": "KKL-88", "sector_id": "sec-b"}'
```
* **Resultado esperado:** HTTP `400 Bad Request` (`{"detail": "Sector sin plazas libres"}`).

---

#### 🔄 Test 6: Reversión de Ticket (Liberar Plaza)
Revertir el ticket emitido en el Test 4:

```bash
curl -i -X POST "http://localhost:8000/v1/tickets/1/revertir" \
  -H "X-API-Key: supersecreto"
```
* **Resultado esperado:** HTTP `200 OK` con `{"id": 1, ..., "estado": "revertido"}`.
* **Verificación interna:** La plaza en `sec-a` fue liberada vía gRPC en Sensores.

---

### 1.3 Prueba de Resiliencia y Modo de Falla (Requisito T7)

Demostrar el comportamiento del sistema cuando el servicio interno gRPC no responde:

1. **Detener el servicio de Sensores:**
   ```bash
   docker stop gRPC_sensores
   ```

2. **Intentar emitir un ticket:**
   ```bash
   curl -i -X POST "http://localhost:8000/v1/tickets/" \
     -H "X-API-Key: supersecreto" \
     -H "Content-Type: application/json" \
     -d '{"patente": "KKL-88", "sector_id": "sec-a"}'
   ```
3. **Resultado esperado:** HTTP `503 Service Unavailable` (`{"detail": "Servicio de sensores temporalmente inactivo"}`).

4. **Restablecer el servicio:**
   ```bash
   docker start gRPC_sensores
   ```

---
---

## 🔬 Parte 2: Opciones de Experimento (Competencia ABET 6 — 40% de la Nota)

La Competencia 6 requiere diseñar un experimento con **método reproducible, datos medidos y conclusiones con juicio de ingeniería**.

---

### 📊 Criterios de Evaluación en la Rúbrica

| Calificación | Descripción |
| :---: | :--- |
| **0 - 1** | No hay experimento o no se presentan datos. |
| **2.0** | Compara dos elementos sin método claro (ej: *"gRPC pesó 30 bytes y JSON 90 bytes"*). |
| **3.0** | Método definido y reproducible. Presenta datos estructurados. |
| **4.0** | **Método riguroso con variables controladas, repetición de mediciones, tabla/gráfico y conclusiones con matices técnicos.** |

---

### 💡 Opción 1: Tamaño de Payload (gRPC/Protobuf vs. REST/JSON) ⭐ *[RECOMENDADO]*

#### Objetivo
Comparar la eficiencia en consumo de ancho de banda entre la serialización binaria de Protobuf (gRPC) y la serialización en texto JSON (REST).

#### Hipótesis
> *"El formato binario de Protocol Buffers reduce el tamaño del payload en al menos un 50% en comparación con JSON sin comprimir, aunque esta brecha se estrecha al aplicar compresión gzip a JSON."*

#### Variables
- **Variable Independiente**: Tamaño del arreglo de datos (1, 10, 50, 100 sectores) y formato de serialización (JSON vs Protobuf vs JSON+gzip).
- **Variable Dependiente**: Tamaño del payload expresado en bytes.

#### Script de Medición (Python)

```python
import json
import gzip
import sensores_pb2

def medir_tamanios(n_elementos):
    # Generar datos simulados
    sectores_json = [
        {
            "sector_id": f"sec-{i}",
            "nombre": f"Sector {i} - Subterráneo Nivel {i}",
            "plazas_totales": 100,
            "plazas_libres": 45
        } for i in range(n_elementos)
    ]
    
    # 1. Serialización JSON
    raw_json = json.dumps(sectores_json).encode('utf-8')
    size_json = len(raw_json)
    
    # 2. Serialización JSON + gzip
    size_json_gzip = len(gzip.compress(raw_json))
    
    # 3. Serialización Protobuf
    list_pb = sensores_pb2.SectoresListResponse()
    for s in sectores_json:
        sec = list_pb.sectores.add()
        sec.sector_id = s["sector_id"]
        sec.nombre = s["nombre"]
        sec.plazas_totales = s["plazas_totales"]
        sec.plazas_libres = s["plazas_libres"]
        
    raw_pb = list_pb.SerializeToString()
    size_pb = len(raw_pb)
    
    return size_json, size_json_gzip, size_pb

# Probar con distintas escalas
print(f"| Cant. Sectores | JSON (bytes) | JSON+Gzip (bytes) | Protobuf (bytes) | Ahorro PB vs JSON |")
print(f"|----------------|--------------|-------------------|------------------|-------------------|")
for n in [1, 5, 10, 25, 50, 100]:
    j, j_gz, pb = medir_tamanios(n)
    ahorro = ((j - pb) / j) * 100
    print(f"| {n:14d} | {j:12d} | {j_gz:17d} | {pb:16d} | {ahorro:16.2f}% |")
```

#### Ejemplo de Estructura de Resultados para el Informe
| Cant. Sectores | REST / JSON (bytes) | JSON + gzip (bytes) | gRPC / Protobuf (bytes) | Ahorro Protobuf vs JSON |
| :---: | :---: | :---: | :---: | :---: |
| 1 | 102 | 95 | 42 | **58.8 %** |
| 10 | 1,020 | 280 | 420 | **58.8 %** |
| 50 | 5,100 | 850 | 2,100 | **58.8 %** |
| 100 | 10,200 | 1,450 | 4,200 | **58.8 %** |

---

### ⚡ Opción 2: Latencia con y sin Caché (Redis)

#### Objetivo
Medir la reducción en el tiempo de respuesta al incorporar Redis como capa de caché para las consultas frecuentes de disponibilidad de sectores.

#### Hipótesis
> *"La incorporación de una caché en memoria (Redis) reduce la latencia de respuesta en las consultas de disponibilidad en más de un 80% al evitar consultas repetitivas a la base de datos."*

#### Metodología
1. Realizar 100 peticiones consecutivas a `ConsultarSector` directo contra SQLite y registrar la latencia promedio.
2. Habilitar caché Redis (Requisito Opcional O1).
3. Realizar 100 peticiones idénticas (con *cache hit*) y registrar la latencia promedio.

---

### ⏱️ Opción 3: Efecto del Timeout en gRPC

#### Objetivo
Analizar el comportamiento y la degradación de la API REST cuando el servicio gRPC experimenta alta latencia o bloqueos.

#### Hipótesis
> *"Implementar un deadline/timeout de 2 segundos en el cliente gRPC evita el agotamiento de workers en FastAPI ante fallos del servicio interno, respondiendo un 503 rápido en lugar de bloquear al usuario indefinidamente."*

#### Metodología
1. Insertar un `time.sleep(5)` en el método `ConsultarSector` del servidor gRPC.
2. Ejecutar 10 peticiones concurrentes a `POST /v1/tickets/` **sin timeout** y medir tiempo de respuesta y tasa de éxito.
3. Configurar `timeout=2.0` en el stub gRPC, repetir la prueba y comparar la disponibilidad de la API REST.

---

### 🚀 Opción 4: Throughput Bajo Carga (Estrés)

#### Objetivo
Determinar la capacidad máxima de procesamiento (RPS - Requests Per Second) del sistema integrado antes de presentar degradación.

#### Metodología
1. Usar herramientas como `autocannon` o `locust`.
2. Simular 10, 50, 100 y 500 usuarios concurrentes emitiendo tickets.
3. Graficar: RPS vs Concurrencia y Latencia p95/p99 vs Concurrencia.
