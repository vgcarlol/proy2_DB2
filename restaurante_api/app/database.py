from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

# Leer URI del entorno
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI no está definido en el archivo .env")

# Crear cliente de conexión
client = AsyncIOMotorClient(MONGO_URI)

# Seleccionar base de datos
db = client.get_default_database() or client["restauranteDB"]
