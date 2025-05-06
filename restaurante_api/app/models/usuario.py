from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class UsuarioBase(BaseModel):
    nombre: str
    email: EmailStr
    contraseña: str
    direccion: str
    telefono: str


class UsuarioCreate(UsuarioBase):
    pass


class Usuario(UsuarioBase):
    id: Optional[str] = Field(alias="_id")

    class Config:
        populate_by_name = True
