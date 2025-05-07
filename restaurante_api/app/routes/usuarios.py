from fastapi import APIRouter, HTTPException, Body
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
#async def listar_usuarios():
    #usuarios = await db.usuarios.find().to_list(length=100)
    #return usuarios
#--- Limite y skip - CRUD ---
async def listar_usuarios(skip: int = 0, limit: int = 100):
    return await db.usuarios.find().skip(skip).limit(limit).to_list(length=limit)


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
 
# proyecciones - CRUD
@router.get("/resumen", response_model=List[dict])
async def resumen_usuarios(skip: int = 0, limit: int = 100):
    cursor = db.usuarios.find(
        {},
        {"nombre": 1, "email": 1, "_id": 0}
    ).skip(skip).limit(limit)
    return await cursor.to_list(length=limit)


#agregacion_simple funcional
@router.get("/usuarios/conteo")
async def contar_usuarios():
    total = await db.usuarios.count_documents({})
    return {"total_usuarios": total}

@router.get("/usuarios/correos-unicos")
async def correos_unicos():
    return await db.usuarios.distinct("email")
@router.post("/bulk", response_model=List[Usuario])
async def crear_usuarios_bulk(usuarios: List[UsuarioCreate]):
    try:
        # Verificar duplicados por email
        emails = [u.email for u in usuarios]
        duplicados = await db.usuarios.find({"email": {"$in": emails}}).to_list(length=len(emails))
        if duplicados:
            usados = [u["email"] for u in duplicados]
            raise HTTPException(status_code=400, detail=f"Emails ya registrados: {usados}")

        usuarios_dict = [u.dict() for u in usuarios]
        result = await db.usuarios.insert_many(usuarios_dict)
        insertados = await db.usuarios.find(
            {"_id": {"$in": result.inserted_ids}}
        ).to_list(length=len(result.inserted_ids))
        return insertados
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al insertar múltiples usuarios: {str(e)}")
from fastapi import Body

@router.delete("/bulk", response_model=dict)
async def eliminar_usuarios_bulk(ids: List[str] = Body(...)):
    object_ids = []
    for id in ids:
        if not ObjectId.is_valid(id):
            raise HTTPException(status_code=400, detail=f"ID inválido: {id}")
        object_ids.append(ObjectId(id))

    result = await db.usuarios.delete_many({"_id": {"$in": object_ids}})
    return {
        "mensaje": "Usuarios eliminados",
        "cantidad_eliminada": result.deleted_count
    }
@router.put("/bulk", response_model=dict)
async def actualizar_usuarios_bulk(usuarios: List[dict] = Body(...)):
    actualizados = 0
    errores = []

    for u in usuarios:
        id = u.get("_id")
        if not id or not ObjectId.is_valid(id):
            errores.append(f"ID inválido: {id}")
            continue
        datos = {k: v for k, v in u.items() if k != "_id"}
        if not datos:
            continue
        result = await db.usuarios.update_one(
            {"_id": ObjectId(id)},
            {"$set": datos}
        )
        actualizados += result.modified_count

    return {
        "mensaje": "Actualización de usuarios completada",
        "cantidad_actualizada": actualizados,
        "errores": errores
    }
