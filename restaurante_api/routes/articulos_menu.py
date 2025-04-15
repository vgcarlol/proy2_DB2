from fastapi import APIRouter, HTTPException
from models.articulo_menu import ArticuloMenu
from database import db
from bson import ObjectId

router = APIRouter(prefix="/menu", tags=["Artículos del Menú"])

@router.post("/")
async def crear_articulo(articulo: ArticuloMenu):
    result = await db.articulos_menu.insert_one(articulo.dict())
    return {"mensaje": "Artículo creado", "id": str(result.inserted_id)}

@router.get("/")
async def listar_articulos():
    articulos = await db.articulos_menu.find().to_list(100)
    for a in articulos:
        a["_id"] = str(a["_id"])
        a["restaurante_id"] = str(a["restaurante_id"])
    return articulos

@router.get("/restaurante/{restaurante_id}")
async def articulos_por_restaurante(restaurante_id: str):
    articulos = await db.articulos_menu.find({
        "restaurante_id": restaurante_id
    }).to_list(100)
    for a in articulos:
        a["_id"] = str(a["_id"])
    return articulos

@router.get("/{id}")
async def obtener_articulo(id: str):
    articulo = await db.articulos_menu.find_one({"_id": ObjectId(id)})
    if not articulo:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")
    articulo["_id"] = str(articulo["_id"])
    return articulo

@router.put("/{id}")
async def actualizar_articulo(id: str, datos: ArticuloMenu):
    result = await db.articulos_menu.update_one(
        {"_id": ObjectId(id)},
        {"$set": datos.dict()}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Artículo no encontrado o sin cambios")
    return {"mensaje": "Artículo actualizado"}

@router.delete("/{id}")
async def eliminar_articulo(id: str):
    result = await db.articulos_menu.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")
    return {"mensaje": "Artículo eliminado"}
