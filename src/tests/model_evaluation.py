import math
from datetime import datetime
import pandas as pd
import numpy as np

from src.database import get_data_as_dataframe, execute_non_query
from src.services.recommender import RecommenderService


def jaccard_index(set_a: set, set_b: set) -> float:
    if not set_a and not set_b:
        return 1.0
    if not set_a or not set_b:
        return 0.0
    inter = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    return inter / union if union > 0 else 0.0


def evaluate_holdout_temporal(proportion_test: float = 0.2, min_history: int = 5, catalog_size: int = 100):
    service = RecommenderService()

    # 1) Preparar lista de usuarios sintéticos (IDs > 17) con al menos `min_history` compras
    sql_users = (
        """
        SELECT u.user_id, COUNT(c.compra_id) as total
        FROM Usuarios u
        JOIN Compras c ON u.user_id = c.user_id
        WHERE u.user_id > 17
        GROUP BY u.user_id
        HAVING COUNT(c.compra_id) >= :min_hist
        """
    )
    df_users = get_data_as_dataframe(sql_users, params={"min_hist": min_history})
    if df_users is None or df_users.empty:
        print("No se encontraron usuarios con el historial mínimo requerido.")
        return

    user_ids = df_users["user_id"].tolist()

    # 2) Verificar si MatrizSimilitud está poblada; si no, entrenar una vez
    df_ms = get_data_as_dataframe("SELECT COUNT(*) as total FROM MatrizSimilitud")
    ms_count = int(df_ms.iloc[0]["total"]) if df_ms is not None and not df_ms.empty else 0
    if ms_count == 0:
        print("MatrizSimilitud vacía. Entrenando modelo antes de la evaluación...")
        service.train_model()

    # Acumuladores de métricas
    jaccard_scores = []
    hit_rates = []
    precision_genre_scores = []
    users_with_genre_prefs = 0
    recommended_items_global = set()

    for uid in user_ids:
        print(f"Evaluando usuario {uid}...")

        # Obtener historial ordenado por fecha (más reciente primero)
        sql_history = (
            "SELECT compra_id, item_id, timestamp FROM Compras WHERE user_id = :uid "
            "ORDER BY timestamp DESC"
        )
        df_hist = get_data_as_dataframe(sql_history, params={"uid": uid})
        if df_hist is None or df_hist.empty:
            print(f" - Usuario {uid} no tiene historial (extraño). Saltando.")
            continue

        total_purchases = len(df_hist)
        test_n = max(1, math.ceil(total_purchases * proportion_test))

        # Test set: 20% más reciente
        df_test = df_hist.head(test_n).copy()
        df_train = df_hist.tail(total_purchases - test_n).copy()

        # Guardar datos del test para reinstertion
        to_restore = df_test.copy()

        # IDs de las compras a eliminar (por compra_id)
        compra_ids = to_restore['compra_id'].astype(int).tolist()

        if not compra_ids:
            print(f" - Usuario {uid} no tiene compras para test. Saltando.")
            continue

        # DELETE seguro: eliminamos solo las filas de este usuario con esos compra_id
        ids_str = ",".join(map(str, compra_ids))
        sql_delete = f"DELETE FROM Compras WHERE compra_id IN ({ids_str}) AND user_id = :uid"

        try:
            # Ejecutar borrado temporal
            deleted = execute_non_query(sql_delete, params={"uid": uid})
            print(f" - Compras eliminadas temporalmente: {deleted}")

            # k dinámico = tamaño del test set
            k_dynamic = len(to_restore)

            # Llamar al recomendador con top_k = k_dynamic
            recs = service.get_recommendations(uid, top_k=k_dynamic)

            # Extraer item_ids recomendados (la estructura puede variar: dicts con item_id)
            rec_item_ids = []
            for r in recs:
                if isinstance(r, dict) and 'item_id' in r:
                    rec_item_ids.append(int(r['item_id']))
                elif isinstance(r, int):
                    rec_item_ids.append(r)

            rec_set = set(rec_item_ids)
            test_set = set(to_restore['item_id'].astype(int).tolist())

            # Métricas
            jacc = jaccard_index(rec_set, test_set)
            hit = 1 if len(rec_set.intersection(test_set)) > 0 else 0

            # Precision de Género
            # Obtener géneros explícitos del usuario
            sql_prefs = "SELECT genero_id FROM PreferenciasUsuario WHERE user_id = :uid"
            df_prefs = get_data_as_dataframe(sql_prefs, params={"uid": uid})
            user_pref_genres = set(df_prefs['genero_id'].tolist()) if df_prefs is not None and not df_prefs.empty else set()

            precision_genre = None
            if rec_item_ids and user_pref_genres:
                # Obtener géneros de los items recomendados
                ids_rec_str = ",".join(map(str, rec_item_ids))
                sql_item_genres = f"SELECT item_id, genero_id FROM ItemGeneros WHERE item_id IN ({ids_rec_str})"
                df_item_genres = get_data_as_dataframe(sql_item_genres)

                # Mapear item -> set(genres)
                item_to_genres = {}
                if df_item_genres is not None and not df_item_genres.empty:
                    for _, row in df_item_genres.iterrows():
                        iid = int(row['item_id'])
                        gid = int(row['genero_id'])
                        item_to_genres.setdefault(iid, set()).add(gid)

                # Calcular cuántos ítems recomendados coinciden con al menos un género preferido
                matches = 0
                for iid in rec_item_ids:
                    genres = item_to_genres.get(iid, set())
                    if not genres.isdisjoint(user_pref_genres):
                        matches += 1

                precision_genre = matches / len(rec_item_ids) if rec_item_ids else 0.0
                users_with_genre_prefs += 1
            else:
                # Si no tiene prefs explícitas o no hubo recomendaciones, definimos precision como None
                precision_genre = None

            # Añadir ítems recomendados al set global para Catalog Coverage
            recommended_items_global.update(rec_set)

            # Guardar métricas
            jaccard_scores.append(jacc)
            hit_rates.append(hit)
            precision_genre_scores.append(precision_genre)

        finally:
            # Restaurar las compras borradas: insertamos usando user_id, item_id y timestamp original
            if not to_restore.empty:
                # Reinsertar en bloque
                inserted = 0
                for _, row in to_restore.iterrows():
                    try:
                        ts = row['timestamp']
                        # Asegurar tipo datetime
                        if isinstance(ts, pd.Timestamp):
                            ts = ts.to_pydatetime()

                        sql_ins = (
                            "INSERT INTO Compras (user_id, item_id, timestamp) "
                            "VALUES (:uid, :iid, :ts)"
                        )
                        execute_non_query(sql_ins, params={"uid": uid, "iid": int(row['item_id']), "ts": ts})
                        inserted += 1
                    except Exception as e:
                        print(f"   [ERROR] Falló reinsertar compra para user {uid}: {e}")
                print(f" - Compras restauradas: {inserted}")

    # Post-proceso de métricas
    avg_jaccard = float(np.mean(jaccard_scores)) if jaccard_scores else 0.0
    avg_hit = float(np.mean(hit_rates)) if hit_rates else 0.0

    # Promedio de precision de género ignorando valores None
    valid_precisions = [p for p in precision_genre_scores if p is not None]
    avg_precision_genre = float(np.mean(valid_precisions)) if valid_precisions else 0.0

    catalog_coverage = (len(recommended_items_global) / float(catalog_size)) * 100.0

    print("\n=== Evaluación Hold-Out Temporal Proporcional (80/20) ===")
    print(f"Usuarios evaluados: {len(jaccard_scores)}")
    print(f"Avg. Jaccard Index: {avg_jaccard:.4f}")
    print(f"Avg. Hit Rate: {avg_hit:.4f}")
    print(f"Avg. Precision (Genre) [sobre usuarios con prefs]: {avg_precision_genre:.4f}")
    print(f"Catalog Coverage: {catalog_coverage:.2f}% ({len(recommended_items_global)} items únicos recomendados)")


if __name__ == "__main__":
    # Ejecutar evaluación
    evaluate_holdout_temporal(proportion_test=0.2, min_history=5, catalog_size=100)
