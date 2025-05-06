from app.database import db

async def crear_indices():
    await db.usuarios.create_index("email", unique=True)

    await db.restaurantes.create_index([("nombre", "text")])
    await db.restaurantes.create_index([("ubicacion", "2dsphere")])

    await db.articulos_menu.create_index("restaurante_id")

    await db.ordenes.create_index([("usuario_id", 1), ("fecha", -1)])
    await db.ordenes.create_index("articulos.articulo_id")

    await db.resenas.create_index([("restaurante_id", 1), ("calificacion", -1)])
    await db.resenas.create_index("comentario", "text")
