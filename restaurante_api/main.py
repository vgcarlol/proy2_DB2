from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import restaurantes, usuarios, articulos_menu, ordenes, resenas


app = FastAPI(title="Sistema de Gestión de Pedidos y Reseñas")

@app.get("/")
async def root():
    return {"mensaje": "Conexión activa con MongoDB Atlas"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # O especifica ["http://127.0.0.1:5500"] si quieres más seguro
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas
app.include_router(restaurantes.router)
app.include_router(usuarios.router)
app.include_router(articulos_menu.router)
app.include_router(ordenes.router)
app.include_router(resenas.router)
