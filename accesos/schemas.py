from pydantic import BaseModel
from typing import Optional

class VehiculoCreate(BaseModel):
    patente: str

class Vehiculo(BaseModel):
    patente: str

    class Config:
        from_attributes = True

class TicketCreate(BaseModel):
    patente: str
    sector_id: str

class Ticket(BaseModel):
    id: int
    patente: str
    sector_id: str
    estado: str

    class Config:
        from_attributes = True
