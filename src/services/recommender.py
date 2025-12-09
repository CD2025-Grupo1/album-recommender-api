import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging
from src.database import get_data_as_dataframe, execute_non_query

logger = logging.getLogger(__name__)

class RecommenderService:
    def __init__(self):

        # Parámetros del modelo híbrido
        self.BOOST_VALUE = 0.1 # valor a sumar si coincide con preferencia explícita

    def get_recommendations(self, user_id: int, top_k: int = 5):
        """
        Decide qué lógica se usa según si es un usuario nuevo o no.
        """
        # Verificar si el usuario tiene historial de compras real
        sql_check = "SELECT COUNT(*) as total FROM Compras WHERE user_id = :uid"
        df_check = get_data_as_dataframe(sql_check, params={"uid": user_id})
        compras_count = df_check.iloc[0]["total"] if df_check is not None else 0

        if compras_count < 1: # cold start
            logger.info(f"Usuario {user_id} es nuevo (0 compras). Usando Cold Start.") 
            raw_recs = self._get_cold_start_items(user_id, top_k)
            return self._enrich_results(raw_recs)
        else:
            logger.info(f"Usuario {user_id} tiene historial ({compras_count} compras). Usando lógica estándar.")
            return self._get_hybrid_recommendations(user_id, top_k, compras_count)

    def _enrich_results(self, recommendations: list):
        """
        Recibe una lista de dicts con 'item_id'.
        Consulta la BD para traer TODOS los datos y formatear al esquema Item.
        """
        if not recommendations:
            return []
            
        # Extraer los IDs para hacer una sola query
        ids = [str(r['item_id']) for r in recommendations]
        if not ids:
            return []
            
        id_str = ",".join(ids)
        
        # Traemos TODO (*) para llenar los atributos
        sql = f"SELECT * FROM Items WHERE item_id IN ({id_str})"
        df_details = get_data_as_dataframe(sql)
        
        if df_details is None or df_details.empty:
            return recommendations
            
        # Convertir a diccionario para búsqueda rápida
        details_map = df_details.set_index('item_id').to_dict(orient='index')
        
        enriched_list = []
        for rec in recommendations:
            iid = rec['item_id']
            if iid in details_map:
                details = details_map[iid]
                
                # Manejo seguro del score (Cold Start no tiene score, tiene ventas)
                score_val = rec.get('score', 0.0)
                
                enriched_item = {
                    "id": iid,
                    "name": details['titulo'], 
                    "attributes": {
                        "artista": details['artista'],
                        "anio": int(details['anio']),
                        "pais": details['pais'],
                        "idioma": details['idioma'],
                        "score_match": score_val 
                    }
                }
                enriched_list.append(enriched_item)
            else:
                # Fallback
                enriched_list.append({
                    "id": iid, 
                    "name": "Desconocido", 
                    "attributes": {}
                }) 
                
        return enriched_list
        
    #  =========================================================================
    #                   LÓGICA DEL SISTEMA HÍBRIDO PONDERADO 
    #  =========================================================================

    def _get_hybrid_recommendations(self, user_id: int, k: int, n_compras: int):
        """
        Implementación del Sistema Híbrido con Pesos Dinámicos según madurez del usuario.
        """

        # 1. Definir Pesos Dinámicos
        # Si tiene pocas compras, el CF es débil -> confiamos en el contenido (CBF)
        # Si tiene muchas, el CF es fuerte -> confiamos en la inteligencia colectiva
        if n_compras <= 15:
            w_cf, w_cbf = 0.3, 0.7 
        elif n_compras <= 25:
            w_cf, w_cbf = 0.5, 0.5
        else:
            w_cf, w_cbf = 0.7, 0.3

        # 2. Obtener candidatos y scores vía Filtrado Colaborativo (Item-Item)
        cf_candidates = self._get_collaborative_filtering_candidates(user_id)
        
        # 3. Obtener candidatos y scores vía Content-Based (Perfil de Usuario)
        cbf_candidates = self._get_content_based_candidates(user_id)
        
        # 4. Combinar resultados, aplicar pesos y booster
        combined_recommendations = self._combine_and_rank(user_id, cf_candidates, cbf_candidates, w_cf, w_cbf)
        
        # 5. Filtrar ítems ya comprados
        final_list = self._filter_purchased_items(user_id, combined_recommendations)
        
        # Fallback de seguridad
        if not final_list:
            logger.warning("El modelo híbrido no retornó candidatos. Usando Fallback.") # 
            return self._get_global_top_sellers(k)
        
        # Recortar al Top K solicitado
        top_k_recs = final_list[:k]
        
        # 6. Enriquecer con Título y Artista
        return self._enrich_results(top_k_recs)

    def get_user_data(self, user_id: int):
        """
        Recupera datos básicos del usuario Y sus géneros favoritos.
        """
        # 1. Datos básicos del usuario
        sql = "SELECT * FROM Usuarios WHERE user_id = :uid"
        df = get_data_as_dataframe(sql, params={"uid": user_id})
        
        if df is not None and not df.empty:
            # Convertimos a dict y tratamos la fecha
            data = df.iloc[0].to_dict()
            data['fecha_creacion'] = str(data['fecha_creacion'])
            
            # 2. Recuperar Preferencias (Géneros favoritos)
            sql_prefs = "SELECT genero_id FROM PreferenciasUsuario WHERE user_id = :uid"
            df_prefs = get_data_as_dataframe(sql_prefs, params={"uid": user_id})
            
            # Si tiene preferencias, las convertimos a lista de ints
            if df_prefs is not None and not df_prefs.empty:
                data['preferencias'] = df_prefs['genero_id'].tolist()
            else:
                data['preferencias'] = []
                
            return data
            
        return None


    
    def train_model(self):
        """
        Calcula la matriz de similitud Item-Item y guarda en la tabla MatrizSimilitud.
        Se debe llamar al iniciar la app y tras compras significativas.
        """
        
        logger.info("[Training] Iniciando re-entrenamiento del modelo CF...")
        
        # 1. Traer datos crudos
        sql = "SELECT user_id, item_id FROM Compras"
        df_compras = get_data_as_dataframe(sql)
        
        if df_compras is None or df_compras.empty:
            logger.warning("[Training] No hay datos suficientes para entrenar.") 
            return

        # 2. Crear matriz en Memoria
        user_item_matrix = df_compras.pivot_table(
            index='user_id', 
            columns='item_id', 
            aggfunc=lambda x: 1, 
            fill_value=0
        )

        # 3. Calcular Similitud del Coseno (Item-Item)
        sim_matrix = cosine_similarity(user_item_matrix.T)
        
        # 4. Preparar datos para inserción masiva
        item_ids = user_item_matrix.columns # obtenemos los IDs reales de las columnas
        updates = []
        
        # Recorremos la matriz triangular superior (evitamos duplicados).
        # Para simplificar la query de lectura, guardaremos la matriz completa.
        num_items = len(item_ids)
        for i in range(num_items):
            for j in range(num_items):
                if i != j: # ignoramos la diagonal principal
                    score = float(sim_matrix[i][j])
                    if score > 0: # Solo guardamos relaciones relevantes
                        updates.append({
                            "ia": int(item_ids[i]), 
                            "ib": int(item_ids[j]), 
                            "sc": score
                        })
        
        # 5. Persistir en Base de Datos 
        if updates:
            logger.info(f"[Training] Guardando {len(updates)} relaciones de similitud en BD...")
            
            # Limpiar tabla
            execute_non_query("DELETE FROM MatrizSimilitud")
            
            # Insertar en lotes
            values_list = [f"({d['ia']}, {d['ib']}, {d['sc']})" for d in updates]
            
            # Insertamos en bloques de 1000 para no romper la query string
            batch_size = 1000
            for k in range(0, len(values_list), batch_size):
                batch = values_list[k:k+batch_size]
                sql_insert = f"INSERT INTO MatrizSimilitud (item_id_a, item_id_b, score) VALUES {','.join(batch)}"
                execute_non_query(sql_insert)
                
            logger.info("[Training] Modelo persistido correctamente.")

    def _get_collaborative_filtering_candidates(self, user_id: int):
        """
        Versión Optimizada: Consulta la BD en lugar de calcular al vuelo.
        """
        logger.debug("Consultando Modelo CF persistido en BD...") 
        
        # Lógica SQL:
        # 1. Encuentra mis compras (Items A)
        # 2. Busca en MatrizSimilitud los Items B que sean parecidos a A.
        # 3. Excluye los que ya compré.
        # 4. Promedia el score.
        
        sql = """
            SELECT 
                ms.item_id_b as item_id,
                AVG(ms.score) as score_cf
            FROM Compras c
            JOIN MatrizSimilitud ms ON c.item_id = ms.item_id_a
            WHERE c.user_id = :uid
            AND ms.item_id_b NOT IN (SELECT item_id FROM Compras WHERE user_id = :uid)
            GROUP BY ms.item_id_b
            ORDER BY score_cf DESC
            LIMIT 20
        """
        
        df_recs = get_data_as_dataframe(sql, params={"uid": user_id})
        
        if df_recs is not None and not df_recs.empty:
            return df_recs.to_dict(orient="records")
        
        logger.debug("No se encontraron candidatos CF.")

        return []

    def _get_content_based_candidates(self, user_id: int):
        """
        Calcula candidatos basándose en la similitud de atributos (Géneros).
        Crea un perfil del usuario promediando sus compras y busca ítems similares (Coseno).
        """
        logger.debug("Calculando: Content-Based Filtering (Perfil de Usuario)...") 
        
        # 1. Obtener Metadatos (Géneros) de todos los ítems
        #    Traemos item_id y el nombre del género para hacer One-Hot Encoding
        sql_items = """
            SELECT i.item_id, g.nombre as genero 
            FROM Items i
            JOIN ItemGeneros ig ON i.item_id = ig.item_id
            JOIN Generos g ON ig.genero_id = g.genero_id
        """
        df_items = get_data_as_dataframe(sql_items)
        
        # 2. Obtener historial de compras del usuario
        sql_bought = "SELECT item_id FROM Compras WHERE user_id = :uid"
        df_bought = get_data_as_dataframe(sql_bought, params={"uid": user_id})
        
        if df_items is None or df_bought is None or df_bought.empty:
            return []
            
        bought_ids = df_bought["item_id"].tolist()
        
        # 3. Construir la Matriz de Características (Item-Features)
        #    Queremos una tabla donde: Índice=Item, Columnas=Géneros, Valor=1 si lo tiene.
        item_features = pd.get_dummies(df_items.set_index('item_id')['genero'])
        item_features = item_features.groupby('item_id').sum()
        
        # 4. Construir el Perfil del Usuario (Vector Promedio)
        #    Filtramos la matriz maestra para quedarnos solo con los ítems que el usuario compró.
        #    Aseguramos que solo usamos items que existen en item_features (intersección).
        user_history_features = item_features.loc[item_features.index.isin(bought_ids)]
        
        if user_history_features.empty:
            logger.warning("El usuario compró ítems sin metadatos de género.") 
            return []
            
        # El "Perfil" es el promedio de los vectores de sus compras.
        # Ej: Si compró 9 rocks y 1 jazz, su vector será 0.9 Rock y 0.1 Jazz.
        user_profile = user_history_features.mean().values.reshape(1, -1)
        
        # 5. Calcular Similitud Coseno (Perfil vs Catálogo)
        #    Comparamos el vector del usuario contra TODOS los ítems del catálogo.
        similarity_scores = cosine_similarity(user_profile, item_features.values)
        
        # 6. Empaquetar resultados
        recommendations = []
        all_item_ids = item_features.index.tolist()
        
        # similarity_scores es una matriz [[score1, score2, ...]], tomamos la fila 0
        for idx, score in enumerate(similarity_scores[0]):
            item_id = all_item_ids[idx]
            
            # Solo recomendamos si no lo ha comprado aún y tiene cierta similitud
            if item_id not in bought_ids and score > 0.1:
                recommendations.append({
                    "item_id": int(item_id),
                    "score_cbf": float(score)
                })
        
        # Ordenamos solo para debug
        recommendations.sort(key=lambda x: x['score_cbf'], reverse=True)
        
        if recommendations: pass
        
        return recommendations

    def _combine_and_rank(self, user_id: int, cf_recs: list, cbf_recs: list, w_cf: float, w_cbf: float):
        """
        Unifica las listas de CF y CBF, aplica pesos y el Booster por preferencias explícitas.
        """
        # 1. Crear diccionario maestro de scores
        #    Estructura: { item_id: {'score': float, 'origin': str} }
        combined_scores = {}

        # Procesar CF ponderado
        for item in cf_recs:
            iid = item['item_id']
            # Normalizamos score CF para que compita
            raw_score = item['score_cf']
            score = raw_score * w_cf
            combined_scores[iid] = score

        # Procesar CBF ponderado
        for item in cbf_recs:
            iid = item['item_id']
            score = item['score_cbf'] * w_cbf
            
            # Si ya existe (vino por CF), sumamos. Si no, inicializamos.
            if iid in combined_scores:
                combined_scores[iid] += score
            else:
                combined_scores[iid] = score

        # 2. Aplicar refuerzo de Preferencias Explícitas

        # Traer géneros explícitos del usuario
        sql_prefs = "SELECT genero_id FROM PreferenciasUsuario WHERE user_id = :uid"
        df_prefs = get_data_as_dataframe(sql_prefs, params={"uid": user_id})
        
        if df_prefs is not None and not df_prefs.empty and combined_scores:
            user_explicit_genres = set(df_prefs["genero_id"].tolist())
            candidate_ids = list(combined_scores.keys())
            
            # Traer géneros de los candidatos
            if candidate_ids:
                sql_item_genres = f"""
                    SELECT item_id, genero_id 
                    FROM ItemGeneros 
                    WHERE item_id IN ({','.join(map(str, candidate_ids))})
                """
                df_item_genres = get_data_as_dataframe(sql_item_genres)
                
                if df_item_genres is not None:
                    # Iterar para ver quién merece el refuerzo
                    for iid in candidate_ids:
                        # Géneros de este ítem
                        genres_of_item = set(df_item_genres[df_item_genres['item_id'] == iid]['genero_id'])
                        
                        # Intersección: ¿Tiene este álbum algún género que yo marqué como favorito?
                        if not genres_of_item.isdisjoint(user_explicit_genres):
                            original = combined_scores[iid]
                            combined_scores[iid] += self.BOOST_VALUE

        # 3. Formatear salida final
        final_list = []
        for iid, score in combined_scores.items():
            final_list.append({
                "item_id": iid,
                "score": score
            })

        # Ordenar descendente por score final
        final_list.sort(key=lambda x: x['score'], reverse=True)
        
        logger.info(f"Ranking híbrido generado con {len(final_list)} candidatos.") 
        return final_list

    def _filter_purchased_items(self, user_id: int, recommendations: list):
        """
        Quita de la lista de recomendaciones los álbumes que el usuario ya compró.
        """
        if not recommendations:
            return []
            
        sql_bought = "SELECT item_id FROM Compras WHERE user_id = :uid"
        df_bought = get_data_as_dataframe(sql_bought, params={"uid": user_id})
        
        ids_bought = df_bought["item_id"].tolist() if df_bought is not None else []
        
        # Filtrar
        clean_list = [r for r in recommendations if r['item_id'] not in ids_bought]
        return clean_list

    # =========================================================================
    #                            LÓGICA COLD START
    # =========================================================================

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
    
    # =========================================================================
    #                      GESTIÓN DE USUARIOS Y TRANSACCIONES
    # =========================================================================
    
    def create_user(self, username: str, attributes: dict):
        """
        Crea usuario con username opcional y procesa atributos (como géneros favoritos).
        """
        # 1. Insertar usuario en la tabla
        sql_user = "INSERT INTO Usuarios (username, fecha_creacion) VALUES (:uname, NOW()) RETURNING user_id"
        
        execute_non_query(
            "INSERT INTO Usuarios (username, fecha_creacion) VALUES (:uname, NOW())",
            params={"uname": username}
        )
        
        # Recuperamos el ID generado
        df = get_data_as_dataframe("SELECT MAX(user_id) as id FROM Usuarios")
        new_user_id = int(df.iloc[0]["id"])

        # 2. Procesar Preferencias (Cold Start)
        generos = attributes.get("generos_id", [])
        
        if generos and isinstance(generos, list):
            for genero_id in generos:
                sql_pref = "INSERT INTO PreferenciasUsuario (user_id, genero_id) VALUES (:uid, :gid)"
                execute_non_query(sql_pref, params={"uid": new_user_id, "gid": genero_id})
            
        return new_user_id

    def add_transaction(self, user_id: int, item_id: int):
        """
        Registra compra y actualiza el modelo.
        """
        # 1. Insertar compra (persistencia de la celda en la matriz User-Item)
        sql = "INSERT INTO Compras (user_id, item_id, timestamp) VALUES (:uid, :iid, NOW())"
        rows = execute_non_query(sql, params={"uid": user_id, "iid": item_id})
        
        if rows > 0:
            # 2. Actualizar la Matriz de Similitud (Item-Item)
            self.train_model() 
            return True
            
        return False