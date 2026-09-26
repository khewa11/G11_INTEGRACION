import grpc
from fastapi import HTTPException
import sensores_pb2
import sensores_pb2_grpc

GRPC_CHANNEL = 'sensores:50051'
TIMEOUT_SECONDS = 5  # Protege al llamador de esperas indefinidas (T7)

def verificar_y_ocupar_plaza(sector_id: str):
    try:
        with grpc.insecure_channel(GRPC_CHANNEL) as channel:
            stub = sensores_pb2_grpc.SensoresServiceStub(channel)
            
            # Consultar disponibilidad en el sector
            response = stub.ConsultarSector(
                sensores_pb2.SectorRequest(sector_id=sector_id),
                timeout=TIMEOUT_SECONDS
            )
            
            if response.plazas_libres <= 0:
                raise HTTPException(status_code=400, detail="Sector sin plazas libres")
                
            # Ocupar plaza
            ocupar_res = stub.OcuparPlaza(sensores_pb2.ModificarPlazaRequest(sector_id=sector_id), timeout=TIMEOUT_SECONDS)
            if not ocupar_res.exito:
                raise HTTPException(status_code=400, detail=ocupar_res.mensaje)
            
            return True
            
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail="Sector inexistente en sensores")
        if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
            raise HTTPException(status_code=503, detail="Timeout: el servicio de sensores no respondió a tiempo")
        # T7: Código 503 indica que el servicio interno está degradado
        raise HTTPException(status_code=503, detail="Servicio de sensores temporalmente inactivo")

def liberar_plaza(sector_id: str):
    try:
        with grpc.insecure_channel(GRPC_CHANNEL) as channel:
            stub = sensores_pb2_grpc.SensoresServiceStub(channel)
            
            # Liberar plaza
            liberar_res = stub.LiberarPlaza(sensores_pb2.ModificarPlazaRequest(sector_id=sector_id), timeout=TIMEOUT_SECONDS)
            if not liberar_res.exito:
                raise HTTPException(status_code=400, detail=liberar_res.mensaje)
                
            return True
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail="Sector inexistente en sensores")
        if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
            raise HTTPException(status_code=503, detail="Timeout: el servicio de sensores no respondió a tiempo")
        raise HTTPException(status_code=503, detail="Servicio de sensores temporalmente inactivo")

    