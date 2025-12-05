from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from src.services.recommender import RecommenderService

router = APIRouter(tags=["Sistema recomendador"])

service = RecommenderService()

# --------------------------------------------
#  Modelos para cumplir especificacion de API
# --------------------------------------------

class UserAttributes(BaseModel):
    fecha_creacion: Optional[str] = None
    preferencias: Optional[List[str]] = None

class UserInput(BaseModel):
    username: str
    attributes: Dict[str, Any] 

    # Configuración para que Swagger muestre este ejemplo por defecto
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "usuario_prueba",
                    "attributes": {
                        "generos_id": [1, 12, 5]
                    }
                }
            ]
        }
    }

class User(BaseModel):
    id: int
    username: str
    attributes: Optional[Dict[str, Any]] = None

class Item(BaseModel):
    id: int
    name: str
    attributes: Optional[Dict[str, Any]] = None

class ItemArray(BaseModel):
    items: List[Item]

class Error(BaseModel):
    code: str
    message: str

# -------------------------------
#           Endpoints
# -------------------------------

@router.get("/", summary="Verificar estado del sistema")
def health_check():
    """
    Devuelve estado 200 si la API está viva.
    """
    return {"status": "ok", "message": "API de Recomendaciones - ACTIVA"}

@router.post("/user", status_code=200, summary="Crear usuario", tags=["Sistema recomendador"])
def create_user(user: UserInput):
    """
    Crea un nuevo usuario.
    En 'attributes' ingresar los IDs de los géneros preferidos (mínimo 3, máximo 5)
    """
    try:
        new_id = service.create_user(user.username, user.attributes)
        
        return User(
            id=new_id,
            username=user.username,
            attributes=user.attributes
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{userId}", response_model=User, summary="Obtener usuario")
def get_user(userId: int = Path(..., description="ID del usuario")):
    """
    Obtener los datos del usuario, incluyendo sus géneros favoritos.
    """
    user_data = service.get_user_data(userId)
    
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Lógica para el nombre: si la BD trajo 'username' (y no es None), lo usamos.
    # Si no, usamos el genérico.
    db_username = user_data.get('username')
    final_username = db_username if db_username else f"Usuario_{user_data['user_id']}"

    return User(
        id=user_data['user_id'],
        username=final_username,
        attributes={
            "fecha_creacion": user_data['fecha_creacion'],
            "generos_favoritos": user_data['preferencias'] 
        }
    )

@router.get("/user/{userId}/recommend", response_model=ItemArray, summary="Recomendar")
def get_recommendations(
    userId: int = Path(..., description="ID del usuario"),
    n: int = Query(..., description="Numero de items a recomendar")
):
    """
    Obtener n recomendaciones para un usuario determinado.
    """
    # Verificamos si existe el usuario primero
    user_data = service.get_user_data(userId)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        recommendations = service.get_recommendations(userId, top_k=n)
        return ItemArray(items=recommendations)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.post("/user/{userId}/transaction", tags=["Sistema recomendador"], summary="Registrar compra")
def register_purchase(
    userId: int = Path(..., description="ID del usuario que compra"), 
    item_id: int = Query(..., description="ID del ítem comprado")
):
    """
    Registra una compra para actualizar el historial y re-entrenar el modelo incrementalmente.
    """
    success = service.add_transaction(userId, item_id)
    
    if success:
        return {"message": "Compra registrada exitosamente"}
    else:
        raise HTTPException(status_code=500, detail="No se pudo registrar la transacción.")