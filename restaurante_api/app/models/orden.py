from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime


class ArticuloPedido(BaseModel):
    articulo_id: str
    cantidad: int
    precioUnitario: float


class OrdenBase(BaseModel):
    usuario_id: str
    restaurante_id: str
    fecha: datetime
    estado: Literal["pendiente", "en preparación", "entregado"]
    total: float
    metodopago: Optional[str] = None
    articulos: List[ArticuloPedido]


class OrdenCreate(OrdenBase):
    pass


class Orden(OrdenBase):
    id: Optional[str] = Field(alias="_id")

    class Config:
        populate_by_name = True
