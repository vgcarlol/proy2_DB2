from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Optional


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


class ArticuloMenuBase(BaseModel):
    restaurante_id: PyObjectId = Field(..., description="ID del restaurante")
    nombre: str
    descripcion: str
    precio: float
    categoria: str

    class Config:
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True


class ArticuloMenuCreate(ArticuloMenuBase):
    pass


class ArticuloMenu(ArticuloMenuBase):
    id: Optional[PyObjectId] = Field(alias="_id")

    class Config:
        json_encoders = {ObjectId: str}
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
