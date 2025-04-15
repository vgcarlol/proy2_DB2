from pydantic import BaseModel, Field
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

class ArticuloMenu(BaseModel):
    restaurante_id: str = Field(..., description="ID del restaurante al que pertenece el artículo")
    nombre: str
    descripcion: str
    precio: float
    categoria: str
