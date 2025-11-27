from fastapi import APIRouter, HTTPException, Query
from typing import List
from src.services.recommender import RecommenderService

router = APIRouter(tags=["Operaciones"])

service = RecommenderService()

# --- Endpoints ---

@router.get("/", summary="Verificar estado del sistema")
def health_check():
    """
    Devuelve estado 200 si la API está viva.
    """
    return {"status": "ok", "message": "API de Recomendaciones - ACTIVA"}

@router.post("/users", status_code=201, summary="Crear nuevo usuario")
def create_new_user(
    generos_id: List[int] = Query(
        ..., 
        title="Géneros Favoritos",
        description="Seleccione los IDs de los géneros (mínimo 3, máximo 5).",
        min_length=3,
        max_length=5, 
        examples=[1, 12, 5] 
    )
):
    """
    Registra un usuario nuevo con al menos 3 géneros preferidos y un máximo de 5.
    """
    try:
        new_id = service.create_user(generos_id)
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
def register_purchase(user_id: int, item_id: int):
    """
    Registra una compra.
    """
    success = service.add_transaction(user_id, item_id)
    if success:
        return {"message": "Compra registrada"}
    else:
        raise HTTPException(status_code=500, detail="Error al registrar transacción")