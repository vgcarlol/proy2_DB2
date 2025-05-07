# Sistema de Gestión de Pedidos y Reseñas de Restaurantes
### VIDEO ENTREGA FINAL
https://youtu.be/cPb1qjPYMY8

Este proyecto implementa una REST API con **FastAPI** y **MongoDB Atlas**, gestiona restaurantes, sus menús, pedidos y reseñas de usuarios.

Documento Fase 1: https://uvggt-my.sharepoint.com/:w:/g/personal/val221164_uvg_edu_gt/EdlV7dPWSZFChZSEh0_iuS8BWpOpzNI-IzMfm_XB0ufFdg?e=qhdysv 
---

##  Tecnologías utilizadas

- Python
- FastAPI
- MongoDB Atlas
- Motor 
- Uvicorn
- Python-dotenv 

---

## Instalación y ejecución

```bash
git clone https://github.com/tu_usuario/tu_repo.git
cd restaurante_api
pip install fastapi uvicorn motor python-dotenv
```

- Crear .env dentro de restaurante_api con:

MONGO_URI=mongodb+srv://"USUARIO":"CONTRASEÑA"@proyecto2.8p68wf5.mongodb.net/?retryWrites=true&w=majority&appName=proyecto2

## Ejecucion
- dentro de restaurante_api:
uvicorn main:app --reload


