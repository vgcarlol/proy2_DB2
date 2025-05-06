from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

# Leer URI del entorno
MONGO_URI = "mongodb+srv://rey22992:1234@proyecto2.8p68wf5.mongodb.net/restauranteDB"

if not MONGO_URI:
    raise ValueError("MONGO_URI no está definido en el archivo .env")

# Crear cliente de conexión
client = AsyncIOMotorClient(MONGO_URI)

# Seleccionar base de datos
db = client["restauranteDB"]
