from pydantic import BaseModel, Field
from typing import List, Optional
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


class Ubicacion(BaseModel):
    type: str = Field(default="Point", const=True)
    coordinates: List[float] = Field(..., description="[longitud, latitud]")

    class Config:
        schema_extra = {
            "example": {
                "type": "Point",
                "coordinates": [-90.5144, 14.6349]
            }
        }


class RestauranteBase(BaseModel):
    nombre: str
    direccion: str
    ubicacion: Ubicacion
    tipoComida: str
    calificacionPromedio: Optional[float] = 0.0  # inicializa en 0

    class Config:
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True


class RestauranteCreate(RestauranteBase):
    pass


class Restaurante(RestauranteBase):
    id: Optional[PyObjectId] = Field(alias="_id")

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True
