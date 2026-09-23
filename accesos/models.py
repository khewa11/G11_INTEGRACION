from sqlalchemy import Column, String, Integer
from database import Base

class Vehiculo(Base):
    __tablename__ = "vehiculos"

    patente = Column(String, primary_key=True, index=True)

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    patente = Column(String, index=True)
    sector_id = Column(String)
    estado = Column(String, default="activo")
