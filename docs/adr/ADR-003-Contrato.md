### ADR D3 - Contrato, versionado y evolución 

**Estado:** Propuesta 

**Contexto:** Los sistemas de Accesos y Sensores necesitan comunicarse de forma estable, pero sus estructuras de datos podrían cambiar en el futuro. Se debe definir cómo evolucionará el contrato sin romper la integración.

**Alternativas consideradas:**

• Opción A: Versionado en la URL (ej: /v1/tickets) para REST y uso de reglas de Backward Compatibility en Protocol Buffers. 

• Opción B: Versionado mediante headers HTTP (Conten-Type) para la API REST.

**Decisión:** Se elige la opción A.

**Justificación:** El versionado en la URL (/v1) es explícito, fácil de enrutar y documentar con OpenAPI. En gRPC, añadir campos nuevos como 'opcional' no rompe a los clientes antiguos, permitiendo evolución continua sin cambiar de versión principal frecuentemente.  

**Costo aceptado:** Mantener múltiples versiones de la API simultáneamente (ej: v1, v2, etc..) implicará duplicar lógica de controladores temporalmente si hay cambios incompatibles.

**Consecuencias:** Los consumidores de la API REST se enterarán de cambios incompatibles a través de la publicación de un nueva versión de la URL y un nuevo contrato OpenAPI. 