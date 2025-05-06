from fastapi import APIRouter, HTTPException
from bson import ObjectId
from typing import List

from app.models.resena import Resena, ResenaCreate
from app.database import db

router = APIRouter(prefix="/resenas", tags=["Reseñas"])


@router.post("/", response_model=Resena)
async def crear_resena(resena: ResenaCreate):
    result = await db.resenas.insert_one(resena.dict())
    creada = await db.resenas.find_one({"_id": result.inserted_id})
    return creada

# --- Limite y skip ordenamiento- CRUD ---
@router.get("/", response_model=List[Resena])
async def listar_resenas(skip: int = 0, limit: int = 100):
    return await db.resenas.find().sort("fecha", -1).skip(skip).limit(limit).to_list(length=limit)

#@router.get("/", response_model=List[Resena])
#async def listar_resenas():
#    resenas = await db.resenas.find().to_list(length=100)
#    return resenas


@router.get("/restaurante/{restaurante_id}", response_model=List[Resena])
async def resenas_por_restaurante(restaurante_id: str):
    if not ObjectId.is_valid(restaurante_id):
        raise HTTPException(status_code=400, detail="ID de restaurante inválido")
    
    resenas = await db.resenas.find({
        "restaurante_id": ObjectId(restaurante_id)
    }).sort("calificacion", -1).to_list(length=100)
    return resenas


@router.get("/{id}", response_model=Resena)
async def obtener_resena(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")

    resena = await db.resenas.find_one({"_id": ObjectId(id)})
    if not resena:
        raise HTTPException(status_code=404, detail="Reseña no encontrada")
    return resena


@router.put("/{id}", response_model=dict)
async def actualizar_resena(id: str, datos: ResenaCreate):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")

    result = await db.resenas.update_one(
        {"_id": ObjectId(id)},
        {"$set": datos.dict()}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Reseña no encontrada o sin cambios")
    return {"mensaje": "Reseña actualizada"}

 
@router.delete("/{id}", response_model=dict)
async def eliminar_resena(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")

    result = await db.resenas.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Reseña no encontrada")
    return {"mensaje": "Reseña eliminada"}


@router.get("/top-restaurantes", response_model=List[dict])
async def top_restaurantes():
    pipeline = [
        {
            "$group": {
                "_id": "$restaurante_id",
                "promedio_calificacion": { "$avg": "$calificacion" },
                "total_resenas": { "$sum": 1 }
            }
        },
        { "$sort": { "promedio_calificacion": -1 } },
        { "$limit": 10 },
        {
            "$lookup": {
                "from": "restaurantes",
                "localField": "_id",
                "foreignField": "_id",
                "as": "restaurante"
            }
        },
        { "$unwind": "$restaurante" },
        {
            "$project": {
                "_id": 0,
                "nombre": "$restaurante.nombre",
                "promedio_calificacion": 1,
                "total_resenas": 1
            }
        }
    ]
    resultado = await db.resenas.aggregate(pipeline).to_list(length=10)
    return resultado
# proyecciones - CRUD
@router.get("/resumen", response_model=List[dict])
async def resumen_resenas(skip: int = 0, limit: int = 100):
    cursor = db.resenas.find(
        {},
        {"usuario_id": 1, "restaurante_id": 1, "calificacion": 1, "_id": 0}
    ).sort("calificacion", -1).skip(skip).limit(limit)
    return await cursor.to_list(length=limit)
