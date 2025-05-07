from fastapi import APIRouter, HTTPException, Body
from bson import ObjectId
from typing import List

from app.database import db
from app.models.orden import Orden, OrdenCreate

router = APIRouter(prefix="/ordenes", tags=["Órdenes"])


@router.post("/", response_model=Orden)
async def crear_orden(orden: OrdenCreate):
    result = await db.ordenes.insert_one(orden.model_dump(mode="python"))
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


#02_agregacion_compleja no funcional
@router.get("/top-usuarios", response_model=List[dict])
async def top_usuarios_por_ordenes():
    pipeline = [
        {"$group": {"_id": "$usuario_id", "total_ordenes": {"$sum": 1}}},
        {"$sort": {"total_ordenes": -1}},
        {"$limit": 5}
    ]
    resultado = db.ordenes.aggregate(pipeline)
    return await resultado.to_list(length=5)
#03_manejo_arrays funcional

@router.put("/{id}/agregar-item")
async def agregar_articulo(id: str, item: dict):
    if not ObjectId.is_valid(id):
        return {"error": "ID inválido"}
    await db.ordenes.update_one(
        {"_id": ObjectId(id)},
        {"$push": {"articulos": item}}
    )
    return {"msg": "Artículo agregado"}

@router.put("/{id}/quitar-item")
async def quitar_articulo(id: str, articulo_id: str):
    if not ObjectId.is_valid(id):
        return {"error": "ID inválido"}
    await db.ordenes.update_one(
        {"_id": ObjectId(id)},
        {"$pull": {"articulos": {"articulo_id": ObjectId(articulo_id)}}}
    )
    return {"msg": "Artículo eliminado"}
#04_embebidos no funcional
@router.get("/{id}/articulos")
async def obtener_articulos_de_orden(id: str):
    if not ObjectId.is_valid(id):
        return {"error": "ID inválido"}
    orden = await db.ordenes.find_one({"_id": ObjectId(id)}, {"articulos": 1, "_id": 0})
    return orden or {"error": "Orden no encontrada"}


@router.post("/bulk", response_model=List[Orden])
async def crear_multiples_ordenes(
    ordenes: List[OrdenCreate] = Body(...)
):
    try:
        # Convertir cada orden a dict con modo "python" para preservar ObjectId
        ordenes_dict = [orden.model_dump(mode="python") for orden in ordenes]

        # Insertar en MongoDB
        result = await db.ordenes.insert_many(ordenes_dict)

        # Recuperar documentos insertados
        documentos = await db.ordenes.find(
            {"_id": {"$in": result.inserted_ids}}
        ).to_list(length=len(result.inserted_ids))

        return documentos

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al insertar múltiples órdenes: {str(e)}")

from fastapi import Body

@router.delete("/bulk", response_model=dict)
async def eliminar_multiples_ordenes(ids: List[str] = Body(...)):
    # Validar y convertir IDs
    object_ids = []
    for id in ids:
        if not ObjectId.is_valid(id):
            raise HTTPException(status_code=400, detail=f"ID inválido: {id}")
        object_ids.append(ObjectId(id))

    # Eliminar documentos
    result = await db.ordenes.delete_many({"_id": {"$in": object_ids}})
    return {
        "mensaje": "Órdenes eliminadas",
        "cantidad_eliminada": result.deleted_count
    }

@router.put("/bulk", response_model=dict)
async def actualizar_multiples_ordenes(ordenes: List[dict] = Body(...)):
    actualizadas = 0
    errores = []

    for orden in ordenes:
        id = orden.get("_id")
        if not id or not ObjectId.is_valid(id):
            errores.append(f"ID inválido: {id}")
            continue

        obj_id = ObjectId(id)
        # Eliminar _id del cuerpo antes de actualizar
        orden_actualizable = {k: v for k, v in orden.items() if k != "_id"}

        result = await db.ordenes.update_one(
            {"_id": obj_id},
            {"$set": orden_actualizable}
        )

        if result.modified_count > 0:
            actualizadas += 1
        elif result.matched_count == 0:
            errores.append(f"No se encontró la orden con ID: {id}")

    return {
        "mensaje": "Actualización de órdenes completada",
        "cantidad_actualizada": actualizadas,
        "errores": errores
    }
@router.get("/top-usuarios", response_model=List[dict], summary="Top 5 usuarios por # de órdenes")
async def top_usuarios_por_ordenes():
    pipeline = [
        {"$group": {"_id": "$usuario_id", "total_ordenes": {"$sum": 1}}},
        {"$sort":  {"total_ordenes": -1}},
        {"$limit": 5},
        {"$lookup": {
            "from": "usuarios",
            "localField": "_id",
            "foreignField": "_id",
            "as": "usuario"
        }},
        {"$unwind": "$usuario"},
        {"$project": {
            "_id": 0,
            "usuario_id": "$_id",
            "nombre":     "$usuario.nombre",
            "email":      "$usuario.email",
            "total_ordenes": 1
        }},
    ]
    docs = await db.ordenes.aggregate(pipeline).to_list(length=5)

    # convierte ObjectId a str
    for d in docs:
        if isinstance(d.get("usuario_id"), ObjectId):
            d["usuario_id"] = str(d["usuario_id"])
    return docs