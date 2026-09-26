# 🚗 Sistema de Gestión de Estacionamiento — Grupo 11

> **Asignatura:** Integración de Sistemas  
> **Institución:** Universidad de Concepción — Facultad de Ingeniería  
> **Dominio:** Forma C — Sistema de Gestión de Estacionamiento  

---

## 📌 1. Descripción General

Este repositorio contiene la solución de integración para la **Operadora de Estacionamientos del Centro**, conectando dos sistemas previamente aislados:

1. **Servicio de Accesos (API REST / FastAPI)**: Gestiona el registro comercial de vehículos y la emisión/reversión de tickets de estacionamiento.
2. **Servicio de Sensores (gRPC / Python)**: Gestiona el estado físico del recinto, controlando la capacidad total y la disponibilidad de plazas en tiempo real.

Cuando se solicita la emisión de un ticket a la API REST de **Accesos**, esta consulta síncronamente mediante **gRPC** al servicio interno de **Sensores** para validar si existen plazas libres antes de autorizar el ingreso.

---

## 🛠️ 2. Arquitectura del Sistema

```text
[ Cliente / Portal Web ]
           │
           │ (HTTP / REST + JSON / Puerto 8000)
           ▼
┌──────────────────────────────────────┐
│       Microservicio ACCESOS          │
│         (FastAPI + SQLite)           │
└──────────────────┬───────────────────┘
                   │
                   │ (gRPC / HTTP/2 + Protobuf / Puerto 50051)
                   ▼
┌──────────────────────────────────────┐
│        Microservicio SENSORES        │
│       (gRPC Server + SQLite)         │
└──────────────────────────────────────┘
```

- **Patrón Arquitectónico**: REST hacia afuera, gRPC hacia adentro (Bounded Context por dominio).
- **Contratos**: `openapi.yaml` (REST) y `proto/sensores.proto` (gRPC).
- **Persistencia**: Bases de datos SQLite independientes (`accesos.db` y `sensores.db`).

---

## 🚀 3. Requisitos e Instrucciones de Ejecución

### Requisitos Previos
- Docker Desktop o Docker Engine con Docker Compose instalado.

### Despliegue del Sistema
Para construir las imágenes y levantar todos los contenedores con un solo comando:

```bash
docker compose up --build
```

Los servicios estarán disponibles en:
- **API REST (Accesos)**: `http://localhost:8000`
- **Servicio gRPC (Sensores)**: `localhost:50051`
- **Documentación Interactive Swagger UI (FastAPI)**: `http://localhost:8000/docs`

Para detener los servicios:
```bash
docker compose down
```

---

## 🔑 4. Autenticación y Seguridad

La API REST requiere la inclusión de una cabecera de autenticación por API Key en cada petición:

- **Header**: `X-API-Key`
- **Valor por defecto**: `supersecreto`

---

## 📡 5. Endpoints y Contratos

### API REST (Accesos)

| Método | Endpoint | Descripción | Requiere Auth |
| :--- | :--- | :--- | :---: |
| `POST` | `/v1/vehiculos/` | Registra un nuevo vehículo | Sí |
| `GET` | `/v1/vehiculos/` | Lista todos los vehículos registrados | Sí |
| `GET` | `/v1/vehiculos/{patente}` | Consulta la información de un vehículo | Sí |
| `POST` | `/v1/tickets/` | Emite un ticket de acceso (valida plazas en Sensores vía gRPC) | Sí |
| `GET` | `/v1/tickets/` | Lista todos los tickets de acceso | Sí |
| `GET` | `/v1/tickets/{ticket_id}` | Consulta la información de un ticket | Sí |
| `POST` | `/v1/tickets/{ticket_id}/revertir` | Libera la plaza y marca el ticket como revertido | Sí |

### Servicio gRPC (Sensores)

| Método RPC | Parámetro Entrada | Respuesta | Descripción |
| :--- | :--- | :--- | :--- |
| `ConsultarSector` | `SectorRequest` | `SectorResponse` | Consulta disponibilidad de plazas en un sector |
| `ListarSectores` | `Empty` | `SectoresListResponse` | Obtiene lista de sectores |
| `OcuparPlaza` | `ModificarPlazaRequest` | `OperacionResponse` | Resta 1 a las plazas libres (atómico) |
| `LiberarPlaza` | `ModificarPlazaRequest` | `OperacionResponse` | Suma 1 a las plazas libres (atómico) |

---

## 📂 6. Estructura del Repositorio

```text
.
├── accesos/                 # Microservicio de Accesos (API REST - FastAPI)
│   ├── routers/             # Endpoints (tickets, vehiculos)
│   ├── database.py          # Configuración SQLite/SQLAlchemy
│   ├── Dockerfile           # Dockerfile del servicio de accesos
│   ├── grpc_client.py       # Cliente gRPC para comunicarse con Sensores
│   ├── models.py            # Modelos ORM SQLAlchemy
│   ├── schemas.py           # Esquemas Pydantic v2
│   └── requirements.txt     # Dependencias Python
├── sensores/                # Microservicio de Sensores (gRPC Server)
│   ├── main.py              # Servidor gRPC y base de datos de sectores
│   ├── Dockerfile           # Dockerfile del servicio de sensores
│   └── requirements.txt     # Dependencias Python
├── proto/                   # Contratos de Protocol Buffers
│   └── sensores.proto       # Definición de servicios y mensajes gRPC
├── docs/                    # Documentación y Decisiones Arquitectónicas
│   └── adr/                 # Architecture Decision Records (ADR-001 a ADR-004)
├── docker-compose.yml       # Orquestación del sistema completo
├── openapi.yaml             # Especificación OpenAPI 3.0.3 de la API REST
└── README.md                # Documentación del proyecto
```

---

## 🤖 7. Declaración del Uso de Asistentes de IA

En cumplimiento con las políticas de integridad académica del encargo, se declara el uso del asistente de IA **Antigravity** (Google DeepMind) durante el desarrollo del proyecto:

1. **¿Para qué se utilizó?**:
   - Asistencia en la identificación y corrección de *race conditions* en sentencias SQL concurrentes en el servidor gRPC.
   - Apoyo en la estructuración de la especificación `openapi.yaml` completa conforme al estándar OpenAPI 3.0.3.
   - Asistencia en la resolución de errores de build de imágenes Docker (nombres de módulos en la compilación de Protocol Buffers).
   - Generación de sugerencias de formato para mensajes de commit y estructuración de la documentación del proyecto.

2. **Verificación Humana**:
   - Todo el código, configuraciones de Docker, contratos `.proto` y especificaciones OpenAPI fueron revisados, probados y verificados manualmente por los integrantes del equipo mediante ejecuciones locales y pruebas de integración.