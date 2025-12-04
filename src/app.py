import uvicorn
import os
import logging
from datetime import datetime
from fastapi import FastAPI
from src.routes import router
from contextlib import asynccontextmanager
from src.services.recommender import RecommenderService

# Configuración de logging
def configure_logging():

    if not os.path.exists('logs'):
        os.makedirs('logs')
    log_filename = datetime.now().strftime('logs/server_%Y-%m-%d_%H-%M-%S.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'), # Guardar en archivo
            logging.StreamHandler() # Mostrar en consola
        ]
    )
    print(f"--> Logs configurados en: {log_filename}")

configure_logging()
logger = logging.getLogger(__name__)

# Definimos los metadatos de los tags
tags_metadata = [{"name": "Operaciones"}]

description = """
API REST desarrollada por el grupo 1 para el Trabajo Práctico Integrador de Ciencia de Datos 2025.
"""

# Ciclo de vida
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("--- INICIANDO SISTEMA RECOMENDADOR DE ÁLBUMES ---") 
    try:
        svc = RecommenderService()
        svc.train_model()
    except Exception as e:
        logger.error(f"Error en entrenamiento inicial: {e}") 
    yield
    logger.info("--- APAGANDO SISTEMA ---")

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