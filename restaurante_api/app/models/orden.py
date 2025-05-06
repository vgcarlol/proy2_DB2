from pydantic import BaseModel, Field
from typing import Optional, List, Literal
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


# Subdocumento embebido en el array de artículos
class ArticuloPedido(BaseModel):
    articulo_id: PyObjectId
    cantidad: int
    precioUnitario: float

    class Config:
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True


class OrdenBase(BaseModel):
    usuario_id: PyObjectId
    restaurante_id: PyObjectId
    fecha: datetime
    estado: Literal["pendiente", "en preparación", "entregado"]
    total: float
    metodopago: Optional[str] = None
    articulos: List[ArticuloPedido]

    class Config:
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True


class OrdenCreate(OrdenBase):
    pass


class Orden(OrdenBase):
    id: Optional[PyObjectId] = Field(alias="_id")

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True
