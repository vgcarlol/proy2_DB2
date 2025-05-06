from fastapi import FastAPI
from routes import restaurantes, usuarios, articulos_menu, ordenes, resenas


app = FastAPI(title="Sistema de Gestión de Pedidos y Reseñas")

@app.get("/")
async def root():
    return {"mensaje": "Conexión activa con MongoDB Atlas"}

# Incluir rutas
app.include_router(restaurantes.router)
app.include_router(usuarios.router)
app.include_router(articulos_menu.router)
app.include_router(ordenes.router)
app.include_router(resenas.router)
