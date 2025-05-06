import csv
import random
from faker import Faker
from datetime import datetime
from bson import ObjectId
import json

faker = Faker()
Faker.seed(42)
random.seed(42)

N_USUARIOS = 200
N_RESTAURANTES = 50
N_ARTICULOS = 300
N_ORDENES = 500
N_RESENAS = 1000

def nuevo_id():
    return str(ObjectId())

# Pre-generar IDs consistentes
usuario_ids = [nuevo_id() for _ in range(N_USUARIOS)]
restaurante_ids = [nuevo_id() for _ in range(N_RESTAURANTES)]
articulo_ids = [nuevo_id() for _ in range(N_ARTICULOS)]
orden_ids = [nuevo_id() for _ in range(N_ORDENES)]

def generar_usuarios():
    with open('usuarios.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['_id','nombre','email','contraseña','direccion','telefono'])
        for uid in usuario_ids:
            writer.writerow([
                uid,
                faker.name(),
                faker.email(),
                faker.password(),
                faker.address().replace("\n", ", "),
                faker.phone_number()
            ])

def generar_restaurantes():
    with open('restaurantes.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['_id','nombre','direccion','ubicacion','tipoComida','calificacionPromedio'])
        for rid in restaurante_ids:
            lon = round(random.uniform(-180, 180), 6)
            lat = round(random.uniform(-90, 90), 6)
            geojson = json.dumps({
                "type": "Point",
                "coordinates": [lon, lat]
            })
            writer.writerow([
                rid,
                faker.company(),
                faker.address().replace("\n", ", "),
                geojson,
                random.choice(['Italiana', 'Mexicana', 'Japonesa', 'Americana', 'China']),
                round(random.uniform(1.0, 5.0), 2)
            ])

def generar_articulos_menu():
    with open('articulos_menu.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['_id','restaurante_id','nombre','descripcion','precio','categoria'])
        for aid in articulo_ids:
            writer.writerow([
                aid,
                random.choice(restaurante_ids),
                faker.word().capitalize(),
                faker.sentence(),
                round(random.uniform(5, 30), 2),
                random.choice(['Entrada', 'Plato fuerte', 'Postre', 'Bebida'])
            ])

def generar_ordenes():
    with open('ordenes.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['_id','usuario_id','restaurante_id','fecha','estado','total','metodopago','articulos'])
        for oid in orden_ids:
            articulos = []
            total = 0
            for _ in range(random.randint(1, 4)):
                art_id = random.choice(articulo_ids)
                cantidad = random.randint(1, 3)
                precio = round(random.uniform(5, 30), 2)
                total += cantidad * precio
                articulos.append({
                    "articulo_id": art_id,
                    "cantidad": cantidad,
                    "precioUnitario": precio
                })
            writer.writerow([
                oid,
                random.choice(usuario_ids),
                random.choice(restaurante_ids),
                faker.date_time_between(start_date='-6M', end_date='now').isoformat(),
                random.choice(["pendiente", "en preparación", "entregado"]),
                round(total, 2),
                random.choice(["efectivo", "tarjeta"]),
                json.dumps(articulos)
            ])

def generar_resenas():
    with open('resenas.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['_id','usuario_id','restaurante_id','orden_id','calificacion','comentario','fecha'])
        for _ in range(N_RESENAS):
            writer.writerow([
                nuevo_id(),
                random.choice(usuario_ids),
                random.choice(restaurante_ids),
                random.choice(orden_ids),
                random.randint(1, 5),
                faker.sentence(),
                faker.date_time_between(start_date='-6M', end_date='now').isoformat()
            ])

if __name__ == "__main__":
    generar_usuarios()
    generar_restaurantes()
    generar_articulos_menu()
    generar_ordenes()
    generar_resenas()
    print("✔️ Archivos CSV generados exitosamente.")
