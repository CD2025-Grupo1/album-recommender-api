import pandas as pd
from src.database import get_data_as_dataframe, execute_non_query

class RecommenderService:
    def __init__(self):
        # Acá van a ir los modelos que usemos
        pass

    def get_recommendations(self, user_id: int, top_k: int = 5):
        """
        LÓGICA MOCK (Ficticia):
        Devuelve simplemente los primeros 5 ítems de la base de datos
        para probar que la conexión funciona.
        """
        query = "SELECT item_id, titulo, artista FROM Items LIMIT :k" # Query simple para probar la conexión
        
        # Usamos nuestro conector
        df = get_data_as_dataframe(query, params={"k": top_k})
        
        if df is not None and not df.empty:
            return df.to_dict(orient="records") # Convertimos el df a una lista de diccionarios 
        else:
            return []

    def create_user(self, generos_preferidos: list[int]):
        """
        Inserta un usuario real en la BD. Devuelve el ID del usuario creado.
        """
        
        sql_user = "INSERT INTO Usuarios (fecha_creacion) VALUES (NOW()) RETURNING user_id;"
        
        execute_non_query("INSERT INTO Usuarios (fecha_creacion) VALUES (NOW())")
        df = get_data_as_dataframe("SELECT MAX(user_id) as id FROM Usuarios") # toma el último ID, simplificación
        new_user_id = int(df.iloc[0]["id"])

        # Insertar Preferencias Explícitas
        for genero_id in generos_preferidos:
            sql_pref = "INSERT INTO PreferenciasUsuario (user_id, genero_id) VALUES (:uid, :gid)"
            execute_non_query(sql_pref, params={"uid": new_user_id, "gid": genero_id})
            
        return new_user_id

    def add_transaction(self, user_id: int, item_id: int):
        """
        Registra una compra real.
        """
        sql = "INSERT INTO Compras (user_id, item_id, timestamp) VALUES (:uid, :iid, NOW())"
        rows = execute_non_query(sql, params={"uid": user_id, "iid": item_id})
        return rows > 0