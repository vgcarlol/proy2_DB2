from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Any
from datetime import datetime
from bson import ObjectId
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema
from pydantic_core.core_schema import ValidationInfo


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            python_schema=core_schema.with_info_plain_validator_function(cls.validate),
            json_schema=core_schema.str_schema()
        )

    @classmethod
    def validate(cls, v: Any, info: ValidationInfo) -> ObjectId:
        if isinstance(v, ObjectId):
            return v
        if ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("ObjectId inválido")


# Subdocumento embebido
class ArticuloPedido(BaseModel):
    articulo_id: PyObjectId
    cantidad: int
    precioUnitario: float

    model_config = {
        "json_encoders": {ObjectId: str},
        "arbitrary_types_allowed": True,
    }


class OrdenBase(BaseModel):
    usuario_id: PyObjectId
    restaurante_id: PyObjectId
    fecha: datetime
    estado: Literal["pendiente", "en preparación", "entregado"]
    total: float
    metodopago: Optional[str] = None
    articulos: List[ArticuloPedido]

    model_config = {
        "json_encoders": {ObjectId: str},
        "arbitrary_types_allowed": True,
    }


class OrdenCreate(OrdenBase):
    pass


class Orden(OrdenBase):
    id: Optional[PyObjectId] = Field(alias="_id")

    model_config = {
        "populate_by_name": True,
        "json_encoders": {ObjectId: str},
        "arbitrary_types_allowed": True,
    }
