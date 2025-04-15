from pydantic import BaseModel, Field
from typing import List, Literal
from datetime import datetime

class ArticuloPedido(BaseModel):
    articulo_id: str
    cantidad: int
    precioUnitario: float

class Orden(BaseModel):
    usuario_id: str
    restaurante_id: str
    fecha: datetime
    estado: Literal["pendiente", "en preparación", "entregado"]
    total: float
    metodopago: Literal["tarjeta", "efectivo"]
    articulos: List[ArticuloPedido]
