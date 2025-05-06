import pandas as pd
from pymongo import MongoClient
from bson import ObjectId
import ast
from datetime import datetime

# Conexión a Atlas
client = MongoClient("mongodb+srv://rey22992:1234@proyecto2.8p68wf5.mongodb.net/")
db = client["restauranteDB"]

# Ayuda: convierte string a ObjectId si parece válido
def str_to_objectid(val):
    if isinstance(val, str) and ObjectId.is_valid(val):
        return ObjectId(val)
    return val

# Cargar CSV y adaptar campos según colección
def cargar_csv(nombre_archivo, nombre_coleccion):
    df = pd.read_csv(nombre_archivo)

    if nombre_coleccion == "usuarios":
        df["_id"] = df["_id"].apply(str_to_objectid)

    elif nombre_coleccion == "restaurantes":
        df["_id"] = df["_id"].apply(str_to_objectid)
        df["calificacionPromedio"] = df["calificacionPromedio"].astype(float)

    elif nombre_coleccion == "articulos_menu":
        df["_id"] = df["_id"].apply(str_to_objectid)
        df["restaurante_id"] = df["restaurante_id"].apply(str_to_objectid)

    elif nombre_coleccion == "ordenes":
        df["_id"] = df["_id"].apply(str_to_objectid)
        df["usuario_id"] = df["usuario_id"].apply(str_to_objectid)
        df["restaurante_id"] = df["restaurante_id"].apply(str_to_objectid)
        df["fecha"] = pd.to_datetime(df["fecha"])
        df["articulos"] = df["articulos"].apply(lambda x: ast.literal_eval(x))  # convierte string JSON a lista dict

        # convertir los ObjectId internos en artículos
        for row in df["articulos"]:
            for art in row:
                art["articulo_id"] = str_to_objectid(art["articulo_id"])

    elif nombre_coleccion == "resenas":
        df["_id"] = df["_id"].apply(str_to_objectid)
        df["usuario_id"] = df["usuario_id"].apply(str_to_objectid)
        df["restaurante_id"] = df["restaurante_id"].apply(str_to_objectid)
        df["orden_id"] = df["orden_id"].apply(str_to_objectid)
        df["fecha"] = pd.to_datetime(df["fecha"])

    documentos = df.to_dict(orient="records")
    db[nombre_coleccion].delete_many({})  # limpia colección
    db[nombre_coleccion].insert_many(documentos)
    print(f"✔️ Cargados {len(documentos)} documentos en '{nombre_coleccion}'")

# Ejecutar cargas
cargar_csv("usuarios.csv", "usuarios")
cargar_csv("restaurantes.csv", "restaurantes")
cargar_csv("articulos_menu.csv", "articulos_menu")
cargar_csv("ordenes.csv", "ordenes")
cargar_csv("resenas.csv", "resenas")
