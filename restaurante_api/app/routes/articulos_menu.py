from fastapi import APIRouter, HTTPException, Body
from bson import ObjectId
from app.database import db
from app.models.articulo_menu import ArticuloMenu, ArticuloMenuCreate
from typing import List

router = APIRouter(prefix="/menu", tags=["Artículos del Menú"])


@router.post("/", response_model=ArticuloMenu)
async def crear_articulo(articulo: ArticuloMenuCreate):
    result = await db.articulos_menu.insert_one(articulo.dict())
    creado = await db.articulos_menu.find_one({"_id": result.inserted_id})
    return creado


@router.get("/", response_model=List[ArticuloMenu])
#async def listar_articulos():
#    articulos = await db.articulos_menu.find().to_list(length=100)
#    return articulos
# # --- Limite y skip y ordenamiento - CRUD ---
async def listar_articulos(skip: int = 0, limit: int = 100):
    return await db.articulos_menu.find().sort("nombre", 1).skip(skip).limit(limit).to_list(length=limit)



#Filtros - CRUD
@router.get("/restaurante/{restaurante_id}", response_model=List[ArticuloMenu])
async def articulos_por_restaurante(restaurante_id: str):
    if not ObjectId.is_valid(restaurante_id):
        raise HTTPException(status_code=400, detail="ID de restaurante inválido")
    
    articulos = await db.articulos_menu.find({
        "restaurante_id": ObjectId(restaurante_id)
    }).to_list(length=100)
    return articulos


@router.get("/{id}", response_model=ArticuloMenu)
async def obtener_articulo(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    articulo = await db.articulos_menu.find_one({"_id": ObjectId(id)})
    if not articulo:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")
    return articulo

 
@router.put("/{id}", response_model=dict)
async def actualizar_articulo(id: str, datos: ArticuloMenuCreate):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    result = await db.articulos_menu.update_one(
        {"_id": ObjectId(id)},
        {"$set": datos.dict()}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Artículo no encontrado o sin cambios")
    return {"mensaje": "Artículo actualizado"}


@router.delete("/{id}", response_model=dict)
async def eliminar_articulo(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")
    
    result = await db.articulos_menu.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")
    return {"mensaje": "Artículo eliminado"}

# proyecciones - CRUD
@router.get("/resumen", response_model=List[dict])
async def resumen_articulos(skip: int = 0, limit: int = 100):
    cursor = db.articulos_menu.find(
        {},
        {"nombre": 1, "precio": 1, "categoria": 1, "_id": 0}
    ).sort("nombre", 1).skip(skip).limit(limit)
    return await cursor.to_list(length=limit)
from fastapi import Body

@router.post("/bulk", response_model=List[ArticuloMenu])
async def crear_articulos_menu_bulk(
    articulos: List[ArticuloMenuCreate] = Body(...)
):
    try:
        articulos_dict = [articulo.dict() for articulo in articulos]
        result = await db.articulos_menu.insert_many(articulos_dict)
        documentos = await db.articulos_menu.find(
            {"_id": {"$in": result.inserted_ids}}
        ).to_list(length=len(result.inserted_ids))
        return documentos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al insertar múltiples artículos: {str(e)}")
@router.delete("/bulk", response_model=dict)
async def eliminar_articulos_menu_bulk(ids: List[str] = Body(...)):
    object_ids = []
    for id in ids:
        if not ObjectId.is_valid(id):
            raise HTTPException(status_code=400, detail=f"ID inválido: {id}")
        object_ids.append(ObjectId(id))
    result = await db.articulos_menu.delete_many({"_id": {"$in": object_ids}})
    return {
        "mensaje": "Artículos eliminados",
        "cantidad_eliminada": result.deleted_count
    }
@router.put("/bulk", response_model=dict)
async def actualizar_articulos_menu_bulk(
    actualizaciones: List[dict] = Body(...)
):
    modificados = 0
    for item in actualizaciones:
        id = item.get("_id")
        if not id or not ObjectId.is_valid(id):
            raise HTTPException(status_code=400, detail=f"ID inválido: {id}")
        data = {k: v for k, v in item.items() if k != "_id"}
        if not data:
            continue
        result = await db.articulos_menu.update_one(
            {"_id": ObjectId(id)},
            {"$set": data}
        )
        modificados += result.modified_count
    return {"mensaje": "Artículos actualizados", "modificados": modificados}
