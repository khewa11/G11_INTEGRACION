from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
import grpc_client
from database import get_db

router = APIRouter(prefix="/tickets", tags=["tickets"])
api_key_header = APIKeyHeader(name="X-API-Key")

def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != "supersecreto":
        raise HTTPException(status_code=403, detail="No autorizado")
    return api_key

@router.post("/", response_model=schemas.Ticket, status_code=201)
def emitir_ticket(ticket: schemas.TicketCreate, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    # 1. Verificar si el vehículo existe (Regla de negocio: el vehículo debe existir para entrar)
    # db_vehiculo = db.query(models.Vehiculo).filter(models.Vehiculo.patente == ticket.patente).first()
    # if not db_vehiculo:
    #     raise HTTPException(status_code=404, detail="Vehículo no registrado")
        
    # 2. Verificar y ocupar plaza vía gRPC (Sensores)
    grpc_client.verificar_y_ocupar_plaza(ticket.sector_id)
    
    # 3. Guardar el ticket
    nuevo_ticket = models.Ticket(patente=ticket.patente, sector_id=ticket.sector_id, estado="activo")
    db.add(nuevo_ticket)
    db.commit()
    db.refresh(nuevo_ticket)
    return nuevo_ticket
