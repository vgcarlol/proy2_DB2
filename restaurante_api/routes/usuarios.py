from fastapi import APIRouter, HTTPException
from models.usuario import Usuario
from database import db
from bson import ObjectId

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.post("/")
async def crear_usuario(usuario: Usuario):
    existente = await db.usuarios.find_one({"email": usuario.email})
    if existente:
        raise HTTPException(status_code=400, detail="El email ya está registrado.")
    resultado = await db.usuarios.insert_one(usuario.dict())
    return {"mensaje": "Usuario creado", "id": str(resultado.inserted_id)}

@router.get("/")
async def listar_usuarios():
    usuarios = await db.usuarios.find().to_list(100)
    for usuario in usuarios:
        usuario["_id"] = str(usuario["_id"])
    return usuarios

@router.get("/{id}")
async def obtener_usuario(id: str):
    usuario = await db.usuarios.find_one({"_id": ObjectId(id)})
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario["_id"] = str(usuario["_id"])
    return usuario

@router.put("/{id}")
async def actualizar_usuario(id: str, datos: Usuario):
    result = await db.usuarios.update_one(
        {"_id": ObjectId(id)},
        {"$set": datos.dict()}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado o sin cambios")
    return {"mensaje": "Usuario actualizado"}

@router.delete("/{id}")
async def eliminar_usuario(id: str):
    result = await db.usuarios.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"mensaje": "Usuario eliminado"}
