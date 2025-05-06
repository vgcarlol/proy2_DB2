from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Optional, Any
from pydantic.json_schema import JsonSchemaValue
from pydantic import GetJsonSchemaHandler


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: Any) -> ObjectId:
        if not ObjectId.is_valid(v):
            raise ValueError("ObjectId inválido")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: Any, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return {"type": "string", "pattern": "^[a-fA-F0-9]{24}$"}


class ArticuloMenu(BaseModel):
    restaurante_id: str
    nombre: str
    descripcion: str
    precio: float
    categoria: str
    id: Optional[str] = Field(alias="_id")  # 👈 ahora acepta strings

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True



class ArticuloMenuCreate(ArticuloMenu):
    pass


class ArticuloMenu(ArticuloMenu):
    id: Optional[PyObjectId] = Field(alias="_id")

    model_config = {
        "json_encoders": {ObjectId: str},
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }
