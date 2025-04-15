from fastapi import APIRouter

router = APIRouter(prefix="/restaurantes", tags=["Restaurantes"])

@router.get("/")
async def test_restaurantes():
    return {"mensaje": "Rutas de restaurantes activas"}
