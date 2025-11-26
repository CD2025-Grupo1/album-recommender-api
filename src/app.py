import uvicorn
from fastapi import FastAPI
from src.routes import router

# Metadatos para la documentación automática (Swagger)
description = """
API del Sistema Recomendador de Álbumes (TPI de Ciencia de Datos 2025 - Grupo 1).
Permite gestionar usuarios, registrar compras y obtener recomendaciones.
"""

app = FastAPI(
    title="Sistema Recomendador de Álbumes",
    description=description,
    version="1.0.0"
)

# Incluir las rutas definidas en routes.py
app.include_router(router)

if __name__ == "__main__":
    # Corre el servidor en localhost:8000
    uvicorn.run("src.app:app", host="127.0.0.1", port=8000, reload=True)