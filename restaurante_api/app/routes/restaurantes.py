from fastapi import APIRouter, HTTPException
from bson import ObjectId
from typing import List
from app.database import db
from app.models.restaurante import Restaurante, RestauranteCreate

router = APIRouter(prefix="/restaurantes", tags=["Restaurantes"])


@router.post("/", response_model=Restaurante)
async def crear_restaurante(data: RestauranteCreate):
    result = await db.restaurantes.insert_one(data.dict())
    nuevo = await db.restaurantes.find_one({"_id": result.inserted_id})
    return nuevo


@router.get("/", response_model=List[Restaurante])
async def listar_restaurantes():
    restaurantes = await db.restaurantes.find().to_list(length=100)
    print(restaurantes)  

    return restaurantes


@router.get("/{id}", response_model=Restaurante)
async def obtener_restaurante(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    restaurante = await db.restaurantes.find_one({"_id": ObjectId(id)})
    if not restaurante:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")
    return restaurante


@router.get("/cercanos/")
async def restaurantes_cercanos(lat: float, lon: float, max_metros: int = 1000):
    restaurantes = await db.restaurantes.find({
        "ubicacion": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "$maxDistance": max_metros
            }
        }
    }).to_list(length=50)
    return restaurantes


@router.put("/{id}", response_model=dict)
async def actualizar_restaurante(id: str, data: RestauranteCreate):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    result = await db.restaurantes.update_one(
        {"_id": ObjectId(id)},
        {"$set": data.dict()}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado o sin cambios")
    return {"mensaje": "Restaurante actualizado"}

 
@router.delete("/{id}", response_model=dict)
async def eliminar_restaurante(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")

    result = await db.restaurantes.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")
    return {"mensaje": "Restaurante eliminado"}
