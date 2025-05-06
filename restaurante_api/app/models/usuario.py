from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("ObjectId inválido")
        return ObjectId(v)
    
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class UsuarioBase(BaseModel):
    nombre: str
    email: EmailStr
    contraseña: str
    direccion: str
    telefono: str

    class Config:
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True


class UsuarioCreate(UsuarioBase):
    pass


class Usuario(UsuarioBase):
    id: Optional[PyObjectId] = Field(alias="_id")

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True
