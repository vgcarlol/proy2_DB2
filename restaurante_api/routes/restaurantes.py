from fastapi import APIRouter
from bson import ObjectId
from database import db  # O tu conector mongo

router = APIRouter(prefix="/restaurantes", tags=["Restaurantes"])

def restaurante_serializer(restaurante) -> dict:
    return {
        "_id": str(restaurante["_id"]),
        "nombre": restaurante.get("nombre"),
        "direccion": restaurante.get("direccion"),
        "telefono": restaurante.get("telefono")
    }

@router.get("/")
async def obtener_restaurantes():
    restaurantes = []
    async for r in db.restaurantes.find():
        restaurantes.append(restaurante_serializer(r))
    return restaurantes
