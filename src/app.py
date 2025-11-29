import uvicorn
from fastapi import FastAPI
from src.routes import router
from contextlib import asynccontextmanager

from src.services.recommender import RecommenderService

# Definimos los metadatos de los tags para que se vean bonitos
tags_metadata = [
    {
        "name": "Operaciones",
    }
]

description = """
API REST desarrollada por el grupo 1 para el Trabajo Práctico Integrador de Ciencia de Datos 2025.
"""

# Definimos el ciclo de vida para entrenar al inicio
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("--- INICIANDO SISTEMA DE RECOMENDACIÓN ---")
    try:
        # Instanciamos una vez para entrenar
        svc = RecommenderService()
        svc.train_model()
    except Exception as e:
        print(f"Error en entrenamiento inicial: {e}")
    yield
    print("--- APAGANDO SISTEMA ---")

app = FastAPI(
    title="Sistema Recomendador de Álbumes",
    description=description,
    version="1.0.0",
    openapi_tags=tags_metadata,
    lifespan=lifespan
)

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("src.app:app", host="127.0.0.1", port=8000, reload=True)