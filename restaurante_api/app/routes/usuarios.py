from fastapi import APIRouter, HTTPException
from app.models.usuario import Usuario, UsuarioCreate
from app.database import db
from bson import ObjectId
from typing import List

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.post("/", response_model=Usuario)
async def crear_usuario(usuario: UsuarioCreate):
    existente = await db.usuarios.find_one({"email": usuario.email})
    if existente:
        raise HTTPException(status_code=400, detail="El email ya está registrado.")

    resultado = await db.usuarios.insert_one(usuario.dict())
    creado = await db.usuarios.find_one({"_id": resultado.inserted_id})
    return creado


@router.get("/", response_model=List[Usuario])
async def listar_usuarios():
    usuarios = await db.usuarios.find().to_list(length=100)
    return usuarios


@router.get("/{id}", response_model=Usuario)
async def obtener_usuario(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")

    usuario = await db.usuarios.find_one({"_id": ObjectId(id)})
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.put("/{id}", response_model=dict)
async def actualizar_usuario(id: str, datos: UsuarioCreate):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")

    result = await db.usuarios.update_one(
        {"_id": ObjectId(id)},
        {"$set": datos.dict()}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado o sin cambios")
    return {"mensaje": "Usuario actualizado"}


@router.delete("/{id}", response_model=dict)
async def eliminar_usuario(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido")

    result = await db.usuarios.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"mensaje": "Usuario eliminado"}
