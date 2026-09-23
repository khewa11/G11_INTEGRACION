from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from database import get_db

router = APIRouter(prefix="/vehiculos", tags=["vehiculos"])
api_key_header = APIKeyHeader(name="X-API-Key")

def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != "supersecreto":
        raise HTTPException(status_code=403, detail="No autorizado")
    return api_key

@router.post("/", response_model=schemas.Vehiculo, status_code=201)
def crear_vehiculo(vehiculo: schemas.VehiculoCreate, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_vehiculo = db.query(models.Vehiculo).filter(models.Vehiculo.patente == vehiculo.patente).first()
    if db_vehiculo:
        raise HTTPException(status_code=400, detail="Vehículo ya registrado")
    nuevo_vehiculo = models.Vehiculo(patente=vehiculo.patente)
    db.add(nuevo_vehiculo)
    db.commit()
    db.refresh(nuevo_vehiculo)
    return nuevo_vehiculo

@router.get("/", response_model=List[schemas.Vehiculo])
def listar_vehiculos(db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    return db.query(models.Vehiculo).all()

@router.get("/{patente}", response_model=schemas.Vehiculo)
def consultar_vehiculo(patente: str, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_vehiculo = db.query(models.Vehiculo).filter(models.Vehiculo.patente == patente).first()
    if not db_vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return db_vehiculo
