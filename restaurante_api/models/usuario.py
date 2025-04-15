from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from bson import ObjectId

# Soporte para ObjectId
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("ObjectId inválido")
        return ObjectId(v)

class Usuario(BaseModel):
    nombre: str
    email: EmailStr
    contraseña: str
    direccion: str
    telefono: str
