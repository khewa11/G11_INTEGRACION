from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
import grpc
import sensores_pb2
import sensores_pb2_grpc

app = FastAPI(version="1.0.0", root_path="/v1")
api_key_header = APIKeyHeader(name="X-API-Key")

# Base de datos simulada para el servicio de Accesos (T5)
db_accesos = {"tickets": [], "vehiculos": []}

def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != "supersecreto":
        raise HTTPException(status_code=403, detail="No autorizado")
    return api_key

@app.post("/tickets")
def emitir_ticket(patente: str, sector_id: str, api_key: str = Depends(get_api_key)):
    # Manejo de fallas de la dependencia gRPC (T7)
    try:
        with grpc.insecure_channel('sensores:50051') as channel:
            stub = sensores_pb2_grpc.SensoresStub(channel)
            response = stub.ConsultarDisponibilidad(
                sensores_pb2.SectorRequest(sector_id=sector_id)
            )
            
            if response.plazas_libres <= 0:
                raise HTTPException(status_code=400, detail="Sector sin plazas libres")
                
            # Llamada para ocupar plaza
            stub.OcuparPlaza(sensores_pb2.SectorRequest(sector_id=sector_id))
            
            nuevo_ticket = {"patente": patente, "sector_id": sector_id, "estado": "activo"}
            db_accesos["tickets"].append(nuevo_ticket)
            return nuevo_ticket
            
    except grpc.RpcError as e:
        # T7: Código 503 indica que el servicio interno está degradado
        raise HTTPException(status_code=503, detail="Servicio de sensores temporalmente inactivo")