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
    # Opcional: Verificar si el vehículo existe
    db_vehiculo = db.query(models.Vehiculo).filter(models.Vehiculo.patente == ticket.patente).first()
    if not db_vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no registrado. Debe crearlo primero.")
        
    # Verificar y ocupar plaza vía gRPC (Sensores)
    grpc_client.verificar_y_ocupar_plaza(ticket.sector_id)
    
    # Guardar el ticket
    nuevo_ticket = models.Ticket(patente=ticket.patente, sector_id=ticket.sector_id, estado="activo")
    db.add(nuevo_ticket)
    db.commit()
    db.refresh(nuevo_ticket)
    return nuevo_ticket

@router.get("/", response_model=List[schemas.Ticket])
def listar_tickets(db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    return db.query(models.Ticket).all()

@router.get("/{ticket_id}", response_model=schemas.Ticket)
def consultar_ticket(ticket_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    return db_ticket

@router.post("/{ticket_id}/revertir", response_model=schemas.Ticket)
def revertir_ticket(ticket_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not db_ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
        
    if db_ticket.estado != "activo":
        raise HTTPException(status_code=400, detail="El ticket ya ha sido revertido o finalizado")
        
    # Liberar la plaza en el sistema de Sensores vía gRPC
    grpc_client.liberar_plaza(db_ticket.sector_id)
    
    # Actualizar estado del ticket
    db_ticket.estado = "revertido"
    db.commit()
    db.refresh(db_ticket)
    
    return db_ticket
