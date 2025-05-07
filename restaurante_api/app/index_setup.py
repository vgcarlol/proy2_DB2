from app.database import db
async def crear_indices():
    # Restaurantes
    await db.restaurantes.create_index({ "nombre": "text" })  # Búsqueda por texto
    #await db.restaurantes.create_index({ "ubicacion": "2dsphere" })  # Búsqueda geoespacial

    # Usuarios
    await db.usuarios.create_index({ "email": 1 }, unique=True)  # Email único

    # Artículos del Menú
    await db.articulos_menu.create_index({ "restaurante_id": 1 })  # Filtro por restaurante

    # Órdenes
    await db.ordenes.create_index({ "usuario_id": 1, "fecha": -1 })  # Compuesto
    await db.ordenes.create_index({ "articulos.articulo_id": 1 })    # Multikey en array embebido

    # Reseñas
    await db.resenas.create_index({ "restaurante_id": 1, "calificacion": -1 })  # Compuesto
    await db.resenas.create_index({ "comentario": "text" })  # Texto

    print("Todos los índices han sido creados exitosamente.")
