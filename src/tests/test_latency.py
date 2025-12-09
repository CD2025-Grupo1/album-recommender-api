import time
import statistics
from fastapi.testclient import TestClient
from src.app import app  # Importamos tu app FastAPI

# Cliente de pruebas (simula requests HTTP)
client = TestClient(app)

def medir_latencia(endpoint: str, descripcion: str, n_consultas: int = 50):
    tiempos = []
    print(f"\n--- Probando: {descripcion} ---")
    print(f"Endpoint: {endpoint} | Consultas: {n_consultas}")

    # 1. Warm-up: Hacemos una request "falsa" para despertar la conexión a BD y cargar caches
    client.get(endpoint)

    # 2. Bucle de medición
    for _ in range(n_consultas):
        inicio = time.perf_counter()
        response = client.get(endpoint)
        fin = time.perf_counter()

        if response.status_code == 200:
            # Convertimos a milisegundos (ms)
            duracion_ms = (fin - inicio) * 1000
            tiempos.append(duracion_ms)
        else:
            print(f"Error {response.status_code}: {response.text}")

    # 3. Reporte
    if tiempos:
        avg = statistics.mean(tiempos)
        min_t = min(tiempos)
        max_t = max(tiempos)
        
        print(f" Promedio: {avg:.2f} ms")
        print(f" Mínimo:  {min_t:.2f} ms")
        print(f" Máximo:  {max_t:.2f} ms")
        
        if avg < 200:
            print("RESULTADO: CUMPLE OBJETIVO (<200ms)")
        else:
            print("RESULTADO: NO CUMPLE")
    else:
        print("No se pudieron completar las peticiones.")

if __name__ == "__main__":
    print("=== TEST DE LATENCIA DE API ===")
    
    # CASO A: Usuario Recurrente (Usa Modelo Híbrido)
    # Usamos User ID 1 (El 'Rockero' del seed, que tiene historial)
    medir_latencia("/user/1/recommend?n=5", "Usuario Recurrente (Híbrido)", n_consultas=50)

    # CASO B: Usuario Nuevo (Usa Cold Start)
    # Usamos User ID 6 (Uno de los de prueba definidos en init_db sin compras)
    medir_latencia("/user/6/recommend?n=5", "Usuario Nuevo (Cold Start)", n_consultas=50)