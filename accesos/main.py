from fastapi import FastAPI
import models
from database import engine
from routers import vehiculos, tickets

# Crea las tablas en la base de datos (SQLite)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    version="1.0.0", 
    root_path="/v1", 
    title="API de Accesos - Estacionamiento"
)

# Registrar los Routers
app.include_router(vehiculos.router)
app.include_router(tickets.router)