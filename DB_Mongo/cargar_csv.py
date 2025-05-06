import pandas as pd
from pymongo import MongoClient

# Conexión a Atlas
client = MongoClient("mongodb+srv://rey22992:1234@proyecto2.8p68wf5.mongodb.net/")
db = client["restauranteDB"]

# Función para cargar e insertar un CSV
def cargar_csv(nombre_archivo, nombre_coleccion):
    df = pd.read_csv(nombre_archivo)
    documentos = df.to_dict(orient="records")
    db[nombre_coleccion].insert_many(documentos)
    print(f"✔️ Cargados {len(documentos)} documentos en {nombre_coleccion}")

# Cargar los archivos CSV
cargar_csv("usuarios.csv", "usuarios")
cargar_csv("restaurantes.csv", "restaurantes")
cargar_csv("articulos_menu.csv", "articulos_menu")
cargar_csv("ordenes.csv", "ordenes")
cargar_csv("resenas.csv", "resenas")
