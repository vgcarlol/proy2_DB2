from pydantic import BaseModel, Field
from typing import Optional


class RestauranteBase(BaseModel):
    nombre: str
    direccion: str
    tipoComida: str
    latitud: float
    longitud: float
    calificacionPromedio: Optional[float] = 0.0


class RestauranteCreate(RestauranteBase):
    pass


class Restaurante(RestauranteBase):
    id: Optional[str] = Field(alias="_id")

    class Config:
        populate_by_name = True
