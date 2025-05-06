from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
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


class ResenaBase(BaseModel):
    usuario_id: PyObjectId
    restaurante_id: PyObjectId
    orden_id: Optional[PyObjectId] = None
    calificacion: int = Field(..., ge=1, le=5)
    comentario: str
    fecha: datetime

    class Config:
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True


class ResenaCreate(ResenaBase):
    pass


class Resena(ResenaBase):
    id: Optional[PyObjectId] = Field(alias="_id")

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True
