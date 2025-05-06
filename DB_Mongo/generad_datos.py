import csv
import random
from faker import Faker
from datetime import datetime, timedelta

faker = Faker()
Faker.seed(42)
random.seed(42)

# Cantidad de documentos
N_USUARIOS = 200
N_RESTAURANTES = 50
N_ARTICULOS = 300
N_ORDENES = 50000
N_RESENAS = 10000

def generar_usuarios():
    with open('usuarios.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['_id','nombre','email','contraseña','direccion','telefono'])
        for i in range(N_USUARIOS):
            writer.writerow([
                f"user{i}",
                faker.name(),
                faker.email(),
                faker.password(),
                faker.address().replace("\n", ", "),
                faker.phone_number()
            ])

def generar_restaurantes():
    with open('restaurantes.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['_id','nombre','direccion','tipoComida','latitud','longitud','calificacionPromedio'])
        for i in range(N_RESTAURANTES):
            writer.writerow([
                f"rest{i}",
                faker.company(),
                faker.address().replace("\n", ", "),
                random.choice(['Italiana', 'Mexicana', 'Japonesa', 'Americana', 'China']),
                round(random.uniform(-90, 90), 6),
                round(random.uniform(-180, 180), 6),
                round(random.uniform(1, 5), 2)
            ])

def generar_articulos_menu():
    with open('articulos_menu.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['_id','restaurante_id','nombre','descripcion','precio','categoria'])
        for i in range(N_ARTICULOS):
            writer.writerow([
                f"art{i}",
                f"rest{random.randint(0, N_RESTAURANTES - 1)}",
                faker.word().capitalize(),
                faker.sentence(),
                round(random.uniform(5, 30), 2),
                random.choice(['Entrada', 'Plato fuerte', 'Postre', 'Bebida'])
            ])

def generar_ordenes():
    with open('ordenes.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['_id','usuario_id','restaurante_id','fecha','estado','total','metodopago','articulos'])
        for i in range(N_ORDENES):
            usuario = f"user{random.randint(0, N_USUARIOS - 1)}"
            restaurante = f"rest{random.randint(0, N_RESTAURANTES - 1)}"
            estado = random.choice(["pendiente", "en preparación", "entregado"])
            metodopago = random.choice(["tarjeta", "efectivo"])
            fecha = faker.date_time_between(start_date='-6M', end_date='now')
            articulos = []
            total = 0
            for _ in range(random.randint(1, 5)):
                art_id = f"art{random.randint(0, N_ARTICULOS - 1)}"
                cantidad = random.randint(1, 3)
                precio = round(random.uniform(5, 30), 2)
                total += cantidad * precio
                articulos.append({'articulo_id': art_id, 'cantidad': cantidad, 'precioUnitario': precio})
            writer.writerow([
                f"ord{i}",
                usuario,
                restaurante,
                fecha.isoformat(),
                estado,
                round(total, 2),
                metodopago,
                str(articulos).replace("'", '"')  # JSON-like format
            ])

def generar_resenas():
    with open('resenas.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['_id','usuario_id','restaurante_id','orden_id','calificacion','comentario','fecha'])
        for i in range(N_RESENAS):
            writer.writerow([
                f"res{i}",
                f"user{random.randint(0, N_USUARIOS - 1)}",
                f"rest{random.randint(0, N_RESTAURANTES - 1)}",
                f"ord{random.randint(0, N_ORDENES - 1)}",
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
    print("✔️ Archivos CSV generados.")
