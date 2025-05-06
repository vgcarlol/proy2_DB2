from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = "mongodb+srv://rey22992:1234@proyecto2.8p68wf5.mongodb.net/restauranteDB"
client = AsyncIOMotorClient(MONGO_URI)
db = client["restauranteDB"]
