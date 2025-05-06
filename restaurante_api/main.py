from fastapi import FastAPI
from app.routes.usuarios import router as usuarios_router
from app.routes.restaurantes import router as restaurantes_router
from app.routes.articulos_menu import router as menu_router
from app.routes.ordenes import router as ordenes_router
from app.routes.resenas import router as resenas_router
from fastapi.middleware.cors import CORSMiddleware
from app.index_setup import crear_indices  # Importar función de índices

app = FastAPI(title="API Restaurante - Proyecto 2")

# Ruta de prueba de conexión
@app.get("/")
async def root():
    return {"mensaje": "API de Restaurante conectada a MongoDB Atlas"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar todos los routers
app.include_router(usuarios_router)
app.include_router(restaurantes_router)
app.include_router(menu_router)
app.include_router(ordenes_router)
app.include_router(resenas_router)

# Crear índices al iniciar
@app.on_event("startup")
async def startup_event():
    await crear_indices()
