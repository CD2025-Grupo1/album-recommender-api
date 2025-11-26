import pandas as pd
from src.database import get_data_as_dataframe, execute_non_query

class RecommenderService:
    def __init__(self):
        # Aquí cargaríamos los modelos entrenados en el futuro
        pass

    def get_recommendations(self, user_id: int, top_k: int = 5):
        """
        LÓGICA MOCK (Ficticia):
        Devuelve simplemente los primeros 5 ítems de la base de datos
        para probar que la conexión funciona.
        """
        # Query simple para probar la conexión
        query = "SELECT item_id, titulo, artista FROM Items LIMIT :k"
        
        # Usamos nuestro conector seguro
        df = get_data_as_dataframe(query, params={"k": top_k})
        
        if df is not None and not df.empty:
            # Convertimos el DataFrame a una lista de diccionarios (JSON friendly)
            return df.to_dict(orient="records")
        else:
            return []

    def create_user(self, generos_preferidos: list[int]):
        """
        Inserta un usuario real en la BD.
        Retorna el ID del usuario creado.
        """
        # 1. Crear Usuario
        sql_user = "INSERT INTO Usuarios (fecha_creacion) VALUES (NOW()) RETURNING user_id;"
        # Nota: execute_non_query devuelve rowcount, pero para obtener ID necesitamos algo más específico.
        # Por simplicidad en este prototipo, insertamos y asumimos el último ID o usamos una query directa.
        # Para hacerlo robusto con nuestro conector actual, insertamos y buscamos el max ID.
        
        execute_non_query("INSERT INTO Usuarios (fecha_creacion) VALUES (NOW())")
        
        # Recuperamos el ID generado (en un entorno real usaríamos RETURNING con fetchone)
        df = get_data_as_dataframe("SELECT MAX(user_id) as id FROM Usuarios")
        new_user_id = int(df.iloc[0]["id"])

        # 2. Insertar Preferencias (Cold Start)
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