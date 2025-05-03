from fastapi import APIRouter, HTTPException
from models.resena import Resena
from database import db
from bson import ObjectId

router = APIRouter(prefix="/resenas", tags=["Reseñas"])

@router.post("/")
async def crear_resena(resena: Resena):
    result = await db.resenas.insert_one(resena.dict())
    return {"mensaje": "Reseña creada", "id": str(result.inserted_id)}

@router.get("/")
async def listar_resenas():
    resenas = await db.resenas.find().to_list(100)
    for r in resenas:
        r["_id"] = str(r["_id"])
    return resenas

@router.get("/restaurante/{restaurante_id}")
async def resenas_por_restaurante(restaurante_id: str):
    resenas = await db.resenas.find({
        "restaurante_id": restaurante_id
    }).sort("calificacion", -1).to_list(100)
    for r in resenas:
        r["_id"] = str(r["_id"])
    return resenas

@router.get("/{id}")
async def obtener_resena(id: str):
    resena = await db.resenas.find_one({"_id": ObjectId(id)})
    if not resena:
        raise HTTPException(status_code=404, detail="Reseña no encontrada")
    resena["_id"] = str(resena["_id"])
    return resena

@router.put("/{id}")
async def actualizar_resena(id: str, datos: Resena):
    result = await db.resenas.update_one(
        {"_id": ObjectId(id)},
        {"$set": datos.dict()}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Reseña no encontrada o sin cambios")
    return {"mensaje": "Reseña actualizada"}

@router.delete("/{id}")
async def eliminar_resena(id: str):
    result = await db.resenas.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Reseña no encontrada")
    return {"mensaje": "Reseña eliminada"}

@router.get("/top-restaurantes")
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
    resultado = await db.resenas.aggregate(pipeline).to_list(10)
    return resultado
