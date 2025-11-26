from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from src.services.recommender import RecommenderService

# Nombre corto y funcional para el grupo de endpoints
router = APIRouter(tags=["Operaciones"])

service = RecommenderService()

# Modelos de Entrada con ejemplos 
class UserCreate(BaseModel):
    generos_id: List[int]

    # Esto hace que en Swagger aparezca data de ejemplo lista para usar
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "generos_id": [1, 12, 5]  # Rock, Hard Rock, Punk
                }
            ]
        }
    }

class TransactionCreate(BaseModel):
    item_id: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "item_id": 31  # Ejemplo "Thriller"
                }
            ]
        }
    }

# Endpoints

@router.get("/", summary="Verificar estado del sistema")
def health_check():
    """
    Devuelve estado 200 si la API está viva.
    """
    return {"status": "ok", "message": "API de Recomendaciones - ACTIVA"}

@router.post("/users", status_code=201, summary="Crear nuevo usuario")
def create_new_user(user: UserCreate):
    """
    Registra un usuario y sus gustos iniciales para poder recomendarle música inmediatamente.
    """
    try:
        new_id = service.create_user(user.generos_id)
        return {"user_id": new_id, "message": "Usuario creado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommend/{user_id}", summary="Obtener recomendaciones")
def get_recommendations(user_id: int):
    """
    Entrega el Top 5 de álbumes sugeridos para el usuario dado.
    """
    items = service.get_recommendations(user_id)
    return {"user_id": user_id, "recommendations": items}

@router.post("/users/{user_id}/transaction", summary="Registrar compra")
def register_purchase(user_id: int, transaction: TransactionCreate):
    """
    Guarda la interacción 'usuario compra ítem'.
    """
    success = service.add_transaction(user_id, transaction.item_id)
    if success:
        return {"message": "Compra registrada"}
    else:
        raise HTTPException(status_code=500, detail="Error al registrar transacción")