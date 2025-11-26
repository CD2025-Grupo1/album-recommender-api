from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from src.services.recommender import RecommenderService

router = APIRouter(tags=["Sistema Recomendador de Álbumes"])

service = RecommenderService()

# --- Modelos de Entrada (Validación de JSON) ---
class UserCreate(BaseModel):
    generos_id: List[int] 

class TransactionCreate(BaseModel):
    item_id: int

# --- Endpoints ---

@router.get("/", summary="Verificar Estado del Sistema")
def health_check():
    """
    Endpoint de monitoreo para asegurar que la API está activa.
    """
    return {"status": "ok", "message": "API de Recomendaciones - ACTIVA"}

@router.post("/users", status_code=201, summary="Crear Nuevo Usuario")
def create_new_user(user: UserCreate):
    """
    **Crea un nuevo usuario** en la base de datos.
    
    - Recibe una lista de IDs de géneros.
    - Registra sus preferencias iniciales para solucionar el *Cold Start*.
    - Retorna el ID del usuario generado.
    """
    try:
        new_id = service.create_user(user.generos_id)
        return {"user_id": new_id, "message": "Usuario creado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommend/{user_id}", summary="Obtener Recomendaciones")
def get_recommendations(user_id: int):
    """
    Genera una lista de **5 álbumes recomendados** para el usuario.
    
    - Si el usuario es nuevo, usa filtrado basado en contenido.
    - Si tiene historial, usa filtrado colaborativo.
    """
    items = service.get_recommendations(user_id)
    return {"user_id": user_id, "recommendations": items}

@router.post("/users/{user_id}/transaction", summary="Registrar Compra")
def register_purchase(user_id: int, transaction: TransactionCreate):
    """
    Registra una transacción de compra.
    
    - **user_id**: ID del usuario que compra.
    - **item_id**: ID del álbum comprado.
    - Esto alimenta la base de datos de conocimiento para futuras recomendaciones.
    """
    success = service.add_transaction(user_id, transaction.item_id)
    if success:
        return {"message": "Compra registrada"}
    else:
        raise HTTPException(status_code=500, detail="Error al registrar transacción")