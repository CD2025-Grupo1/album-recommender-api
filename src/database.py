import os
import logging
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from typing import Optional, Dict, Any

# Configuración de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno y configurar conexión con BD
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

if not all([DB_USER, DB_HOST, DB_NAME]): # validar que las variables críticas estén presentes
    logger.error("Faltan variables de entorno críticas para la Base de Datos.")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

def get_data_as_dataframe(query_str: str, params: Optional[Dict[str, Any]] = None) -> Optional[pd.DataFrame]:
    """
    Ejecuta una consulta SELECT y devuelve los resultados en un DataFrame de Pandas.
    """
    try:
        with engine.connect() as connection:
            df = pd.read_sql(text(query_str), connection, params=params)
            return df
    except Exception as e:
        logger.error(f"Error ejecutando consulta de lectura: {e}")
        return None

def execute_non_query(query_str: str, params: Optional[Dict[str, Any]] = None) -> int:
    """
    Para operaciones de escritura (INSERT, UPDATE, DELETE).
    Maneja transacciones automáticamente. Retorna la cantidad de filas afectadas.
    """
    try:
        with engine.connect() as connection:
            trans = connection.begin()
            try:
                result = connection.execute(text(query_str), params or {})
                trans.commit()
                logger.info("Operación de escritura exitosa.")
                return result.rowcount #  devuelve cuántas filas fueron afectadas
            except Exception as e:
                trans.rollback()
                logger.error(f"Error en transacción, se hizo rollback: {e}")
                raise e # Re-lanzamos el error para que la API se entere que falló
    except Exception as e:
        logger.error(f"Error de conexión durante escritura: {e}")
        return 0