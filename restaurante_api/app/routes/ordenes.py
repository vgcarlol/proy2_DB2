from fastapi import APIRouter, HTTPException
from bson import ObjectId
from typing import List

from app.database import db
from app.models.orden import Orden, OrdenCreate

router = APIRouter(prefix="/ordenes", tags=["Órdenes"])


@router.post("/", response_model=Orden)
async def crear_orden(orden: OrdenCreate):
    result = await db.ordenes.insert_one(orden.dict())
    creada = await db.ordenes.find_one({"_id": result.inserted_id})
    return creada


@router.get("/", response_model=List[Orden])
#async def listar_ordenes():
    #ordenes = await db.ordenes.find().to_list(length=100)
    #return ordenes
async def listar_ordenes(skip: int = 0, limit: int = 100):#Limite y skip - CRUD ---
    return await db.ordenes.find().skip(skip).limit(limit).to_list(length=limit)

# Filtros - - CRUD
@router.get("/usuario/{usuario_id}", response_model=List[Orden])
async def ordenes_por_usuario(usuario_id: str):
    if not ObjectId.is_valid(usuario_id):
        raise HTTPException(status_code=400, detail="ID de usuario inválido")
    
    ordenes = await db.ordenes.find(
        {"usuario_id": ObjectId(usuario_id)}
        # Filtros - CRUD
    ).sort("fecha", -1).to_list(length=100)
    return ordenes


@router.get("/{id}", response_model=Orden)
async def obtener_orden(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    orden = await db.ordenes.find_one({"_id": ObjectId(id)})
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return orden


@router.put("/{id}", response_model=dict)
async def actualizar_orden(id: str, datos: OrdenCreate):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")

    result = await db.ordenes.update_one(
        {"_id": ObjectId(id)},
        {"$set": datos.dict()}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Orden no encontrada o sin cambios")
    return {"mensaje": "Orden actualizada"}


@router.delete("/{id}", response_model=dict)
async def eliminar_orden(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")

    result = await db.ordenes.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return {"mensaje": "Orden eliminada"}
# proyecciones - CRUD
@router.get("/resumen", response_model=List[dict])
async def resumen_ordenes(skip: int = 0, limit: int = 100):
    cursor = db.ordenes.find(
        {},
        {"usuario_id": 1, "fecha": 1, "total": 1, "_id": 0}
    ).sort("fecha", -1).skip(skip).limit(limit)
    return await cursor.to_list(length=limit)
