from fastapi import APIRouter, HTTPException
from models.orden import Orden
from database import db
from bson import ObjectId

router = APIRouter(prefix="/ordenes", tags=["Órdenes"])

@router.post("/")
async def crear_orden(orden: Orden):
    result = await db.ordenes.insert_one(orden.dict())
    return {"mensaje": "Orden creada", "id": str(result.inserted_id)}

@router.get("/")
async def listar_ordenes():
    ordenes = await db.ordenes.find().to_list(100)
    for o in ordenes:
        o["_id"] = str(o["_id"])
        o["usuario_id"] = str(o["usuario_id"])
        o["restaurante_id"] = str(o["restaurante_id"])
        for a in o["articulos"]:
            a["articulo_id"] = str(a["articulo_id"])
    return ordenes

@router.get("/usuario/{usuario_id}")
async def obtener_ordenes_por_usuario(usuario_id: str):
    ordenes = await db.ordenes.find({"usuario_id": usuario_id}).sort("fecha", -1).to_list(100)
    for o in ordenes:
        o["_id"] = str(o["_id"])
    return ordenes

@router.get("/{id}")
async def obtener_orden(id: str):
    orden = await db.ordenes.find_one({"_id": ObjectId(id)})
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    orden["_id"] = str(orden["_id"])
    return orden

@router.put("/{id}")
async def actualizar_estado(id: str, nueva_data: Orden):
    result = await db.ordenes.update_one(
        {"_id": ObjectId(id)},
        {"$set": nueva_data.dict()}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Orden no encontrada o sin cambios")
    return {"mensaje": "Orden actualizada"}

@router.delete("/{id}")
async def eliminar_orden(id: str):
    result = await db.ordenes.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return {"mensaje": "Orden eliminada"}

@router.get("/top-platillos")
async def top_platillos():
    pipeline = [
        {"$unwind": "$articulos"},
        {"$group": {
            "_id": "$articulos.articulo_id",
            "total_vendido": {"$sum": "$articulos.cantidad"}
        }},
        {"$sort": {"total_vendido": -1}},
        {"$limit": 10},
        {"$lookup": {
            "from": "articulos_menu",
            "localField": "_id",
            "foreignField": "_id",
            "as": "articulo"
        }},
        {"$unwind": "$articulo"},
        {"$project": {
            "_id": 0,
            "articulo": "$articulo.nombre",
            "total_vendido": 1
        }}
    ]
    resultado = await db.ordenes.aggregate(pipeline).to_list(10)
    return resultado
