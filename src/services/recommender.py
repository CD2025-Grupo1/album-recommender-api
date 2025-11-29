import pandas as pd
from src.database import get_data_as_dataframe, execute_non_query

class RecommenderService:
    def __init__(self):
        pass

    def get_recommendations(self, user_id: int, top_k: int = 5):
        """
        Decide qué lógica se usa según si es un usuario nuevo o no.
        """
        # Verificar si el usuario tiene historial de compras real
        sql_check = "SELECT COUNT(*) as total FROM Compras WHERE user_id = :uid"
        df_check = get_data_as_dataframe(sql_check, params={"uid": user_id})
        compras_count = df_check.iloc[0]["total"] if df_check is not None else 0

        if compras_count < 1: # cold start
            print(f"Usuario {user_id} es nuevo (0 compras). Usando Cold Start.")
            return self._get_cold_start_items(user_id, top_k)
        else:
            # acá va lógica colaborativa (no implementada aún)
            print(f"Usuario {user_id} tiene historial. Usando lógica estándar.")
            return self._get_cold_start_items(user_id, top_k) # Fallback temporal

    def _get_cold_start_items(self, user_id: int, k: int):
        """
        Estrategia Mejorada: Round Robin por Género.
        Garantiza diversidad iterando sobre cada género preferido.
        """
        # Obtener géneros
        sql_prefs = "SELECT genero_id FROM PreferenciasUsuario WHERE user_id = :uid"
        df_prefs = get_data_as_dataframe(sql_prefs, params={"uid": user_id})
        
        if df_prefs is None or df_prefs.empty:
            return self._get_global_top_sellers(k)
            
        mis_generos = df_prefs["genero_id"].tolist()
        
        # Round Robin
        candidates = []
        
        # Calculamos cuántos traer por género para tener de sobra 
        # (ej: si pide 5 y tiene 2 géneros, traemos 3 de c/u)
        limit_per_genre = (k // len(mis_generos)) + 2 
        
        for gid in mis_generos:
            # Query específica para CADA género
            sql_genre = """
                SELECT 
                    i.item_id, i.titulo, i.artista, COUNT(c.compra_id) as ventas
                FROM Items i
                JOIN ItemGeneros ig ON i.item_id = ig.item_id
                LEFT JOIN Compras c ON i.item_id = c.item_id
                WHERE ig.genero_id = :gid
                GROUP BY i.item_id, i.titulo, i.artista
                ORDER BY ventas DESC
                LIMIT :lim
            """
            df_g = get_data_as_dataframe(sql_genre, params={"gid": gid, "lim": limit_per_genre})
            
            if df_g is not None and not df_g.empty:
                # Convertimos a lista de dicts y la agregamos a una lista de listas
                candidates.append(df_g.to_dict(orient="records"))
        
        # Mezclar resultados
        final_recommendations = []
        keep_going = True
        idx = 0
        
        # Mientras no hayamos llenado el cupo K y sigamos teniendo ítems para sacar
        while len(final_recommendations) < k and keep_going:
            keep_going = False
            for genre_list in candidates:
                if idx < len(genre_list):
                    item = genre_list[idx]
                    # Evitar duplicados (un álbum podría estar en dos géneros)
                    if item["item_id"] not in [x["item_id"] for x in final_recommendations]:
                        final_recommendations.append(item)
                        keep_going = True
                    
                    if len(final_recommendations) >= k:
                        break
            idx += 1
            
        # Relleno de seguridad: si no llegamos a K por escasez, rellenamos con populares globales
        if len(final_recommendations) < k:
            needed = k - len(final_recommendations)
            global_top = self._get_global_top_sellers(k + len(final_recommendations)) # exceso por las dudas
            
            for item in global_top:
                # Agregar si no fue recomendado ya
                if item["item_id"] not in [x["item_id"] for x in final_recommendations]:
                    final_recommendations.append(item)
                    if len(final_recommendations) >= k:
                        break
                        
        return final_recommendations

    def _get_global_top_sellers(self, k: int):
        """
        Fallback: los más vendidos de toda la tienda sin importar género.
        """
        sql = """
            SELECT i.item_id, i.titulo, i.artista, COUNT(c.compra_id) as ventas
            FROM Items i
            LEFT JOIN Compras c ON i.item_id = c.item_id
            GROUP BY i.item_id, i.titulo, i.artista
            ORDER BY ventas DESC
            LIMIT :limit
        """
        df = get_data_as_dataframe(sql, params={"limit": k})
        return df.to_dict(orient="records") if df is not None else []
    
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