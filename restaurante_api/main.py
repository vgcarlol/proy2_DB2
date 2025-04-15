from fastapi import FastAPI
from routes import restaurantes 

app = FastAPI(title="Sistema de Gestión de Pedidos y Reseñas")

@app.get("/")
async def root():
    return {"mensaje": "Conexión activa con MongoDB Atlas"}

# Incluir rutas
app.include_router(restaurantes.router)
