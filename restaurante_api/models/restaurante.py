from fastapi import APIRouter, HTTPException
from models.restaurante import Restaurante
from database import db
from bson import ObjectId

# Se define el router para el grupo de rutas relacionadas a "restaurantes"
router = APIRouter(prefix="/restaurantes", tags=["Restaurantes"])

# Crear un nuevo restaurante (POST)
@router.post("/")
async def crear_restaurante(restaurante: Restaurante):
    # Inserta el restaurante como documento en la colección
    result = await db.restaurantes.insert_one(restaurante.dict())
    return {"mensaje": "Restaurante creado", "id": str(result.inserted_id)}

# Listar todos los restaurantes (GET)
@router.get("/")
async def listar_restaurantes():
    # Trae hasta 100 restaurantes de la base de datos
    restaurantes = await db.restaurantes.find().to_list(100)
    # Convierte los ObjectId a string para que puedan ser serializados en JSON
    for r in restaurantes:
        r["_id"] = str(r["_id"])
    return restaurantes

# Obtener un restaurante por su ID (GET)
@router.get("/{id}")
async def obtener_restaurante(id: str):
    # Busca el restaurante por su ObjectId
    restaurante = await db.restaurantes.find_one({"_id": ObjectId(id)})
    if not restaurante:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")
    restaurante["_id"] = str(restaurante["_id"])
    return restaurante

# Actualizar un restaurante por ID (PUT)
@router.put("/{id}")
async def actualizar_restaurante(id: str, datos: Restaurante):
    # Actualiza los campos del restaurante con los datos recibidos
    result = await db.restaurantes.update_one(
        {"_id": ObjectId(id)},
        {"$set": datos.dict()}
    )
    # Si no se actualizó ningún documento, se lanza un error
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado o sin cambios")
    return {"mensaje": "Restaurante actualizado"}

# Eliminar un restaurante por ID (DELETE)
@router.delete("/{id}")
async def eliminar_restaurante(id: str):
    # Elimina el restaurante por su ObjectId
    result = await db.restaurantes.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")
    return {"mensaje": "Restaurante eliminado"}
