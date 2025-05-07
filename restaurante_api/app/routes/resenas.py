from fastapi import APIRouter, HTTPException, Body
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
@router.post("/bulk", response_model=List[Resena])
async def crear_multiples_resenas(resenas: List[ResenaCreate]):
    try:
        resenas_dict = [r.model_dump(mode="python") for r in resenas]
        result = await db.resenas.insert_many(resenas_dict)
        insertadas = await db.resenas.find(
            {"_id": {"$in": result.inserted_ids}}
        ).to_list(length=len(result.inserted_ids))
        return insertadas
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al insertar múltiples reseñas: {str(e)}")
@router.delete("/bulk", response_model=dict)
async def eliminar_multiples_resenas(ids: List[str] = Body(...)):
    object_ids = []
    for id in ids:
        if not ObjectId.is_valid(id):
            raise HTTPException(status_code=400, detail=f"ID inválido: {id}")
        object_ids.append(ObjectId(id))

    result = await db.resenas.delete_many({"_id": {"$in": object_ids}})
    return {
        "mensaje": "Reseñas eliminadas",
        "cantidad_eliminada": result.deleted_count
    }
@router.put("/bulk", response_model=dict)
async def actualizar_multiples_resenas(resenas: List[dict] = Body(...)):
    actualizadas = 0
    errores = []

    for resena in resenas:
        id = resena.get("_id")
        if not id or not ObjectId.is_valid(id):
            errores.append(f"ID inválido: {id}")
            continue

        obj_id = ObjectId(id)
        cuerpo_actualizacion = {k: v for k, v in resena.items() if k != "_id"}

        result = await db.resenas.update_one(
            {"_id": obj_id},
            {"$set": cuerpo_actualizacion}
        )

        if result.modified_count > 0:
            actualizadas += 1
        elif result.matched_count == 0:
            errores.append(f"No se encontró la reseña con ID: {id}")

    return {
        "mensaje": "Actualización de reseñas completada",
        "cantidad_actualizada": actualizadas,
        "errores": errores
    }
