from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Resena(BaseModel):
    usuario_id: str
    restaurante_id: str
    orden_id: Optional[str] = None
    calificacion: int = Field(..., ge=1, le=5)
    comentario: str
    fecha: datetime
