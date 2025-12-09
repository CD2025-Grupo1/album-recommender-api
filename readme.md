# Sistema Recomendador de Álbumes - TPI Ciencia de Datos 2025

Este repositorio contiene la implementación de una API RESTful desarrollada bajo la metodología CRISP-DM para un sistema de recomendación de álbumes musicales. El objetivo del proyecto es personalizar la experiencia de usuario y aumentar las ventas proyectadas en un 10% para el próximo ciclo comercial.

Realizado por los integrantes del grupo 1 de Ciencia de Datos 2025.

## Descripción del Proyecto

El sistema funciona con un catálogo fijo de 100 álbumes clásicos y modernos y utiliza un enfoque híbrido que evoluciona con el usuario:
1.  **Cold Start:** para usuarios nuevos, utiliza preferencias explícitas (géneros favoritos) y una estrategia de *Round Robin* para garantizar diversidad.
2.  **Usuarios Recurrentes:** Implementa un Sistema Híbrido Ponderado que combina:
    * **Filtrado Colaborativo (Item-Item):** Recomendaciones basadas en patrones de compra de la comunidad (Matriz de Similitud).
    * **Content-Based Filtering:** Recomendaciones basadas en el perfil de gustos del usuario (Vectores de Géneros).

La ponderación entre estos modelos es dinámica y se ajusta automáticamente según el historial de compras del usuario.

---

## Instalación y Configuración

Seguí estos pasos para levantar el proyecto en tu máquina local.

### Prerrequisitos
* Python 3.9 o superior.
* PostgreSQL instalado y ejecutándose.

### Paso a Paso

1.  **Clonar el repositorio y crear entorno virtual:**
```bash
# En Windows
python -m venv venv
.\venv\Scripts\activate

# En Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

2.  **Instalar dependencias:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

3.  **Configurar Variables de Entorno:**
Crear un archivo ".env" en la raíz del proyecto (junto a este README) y definir las credenciales locales. Ejemplo de contenido:
```ini
    DB_HOST=localhost
    DB_PORT=5433 # generalmente se usa 5432
    DB_NAME=CD_TPI
    DB_USER=postgres
    DB_PASSWORD=admin
```

4.  **Configuración de la Base de Datos:**
* **Crear BD:** acceder al gestor de base de datos y crear una base vacía con el nombre definido en el paso anterior (ej: CD_TPI)
* **Inicializar Esquema:**: ejecutar el script SQL de inicialización que se encuentra en archivo init_db.sql. Este creará las tablas, insertará el catálogo completo y algunos usuarios para un funcionamiento con lo mínimo indispensable. 
* **Poblar Datos (Seeder):** ejecutar el script SQL seeder de la misma carpeta. Este poblará la base de datos con más de 200 usuarios con más de 50 compras cada uno. Esto asegura un funcionamiento que simula la realidad.


5.  **Ejecutar la API:**
    ```bash
    python -m src.app
    ```

## API Reference

La documentación interactiva (Swagger UI) está disponible en: `http://127.0.0.1:8000/docs`.

### Endpoints Principales

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `POST` | `/user` | **Crear Usuario:** Registra un nuevo usuario recibiendo `username` y `attributes` (incluyendo géneros para Cold Start). |
| `GET` | `/user/{userId}` | **Obtener Usuario:** Devuelve los datos básicos del usuario y sus géneros favoritos guardados. |
| `GET` | `/user/{userId}/recommend` | **Obtener Recomendaciones:** Devuelve una lista de *n* álbumes sugeridos para el usuario. |
| `POST` | `/user/{userId}/transaction` | **Registrar Compra:** Guarda una transacción, actualizando el historial y el entrenamiento incremental. |
| `GET` | `/` | **Health Check:** Verifica que la API esté activa. |

---

## Arquitectura del Modelo

La lógica de recomendación se encuentra en `src/services/recommender.py`.

### Estrategia Híbrida Dinámica
El sistema decide qué peso dar al *Filtrado Colaborativo (CF)* y al *Basado en Contenido (CBF)* según el historial del usuario ($N$ compras):

* **Exploración ($N \le 15$):** 70% CBF / 30% CF. Se priorizan los gustos del usuario sobre la tendencia global.
* **Transición ($15 < N \le 25$):** 50% CBF / 50% CF. Balanceo de estrategias.
* **Explotación ($N > 25$):** 30% CBF / 70% CF. El sistema confía más en la inteligencia colectiva y patrones ocultos.

### Booster
Adicionalmente, se aplica un "refuerzo" a los ítems candidatos que coinciden explícitamente con los géneros declarados por el usuario al registrarse, asegurando que sus intereses principales siempre tengan relevancia.

---

## Evaluación y Métricas

Se incluye un script de validación en `src/tests/model_evaluation.py` que utiliza una estrategia de **Hold-Out Temporal** (separa el 20% de las últimas compras de cada usuario para test).

Métricas utilizadas:
* **Hit Rate:** Porcentaje de veces que el ítem real comprado apareció en las recomendaciones.
* **Jaccard Index:** Similitud entre el conjunto recomendado y el conjunto realmente comprado.
* **Catalog Coverage:** Porcentaje del catálogo total que el sistema es capaz de recomendar (evita sesgos de popularidad extrema).

Para ejecutar la evaluación:
```bash
python -m src.tests.model_evaluation
```

Además, el script `src/tests/test_latency.py` está diseñado para medir la latencia, uno de los principales criterios de éxito del proyecto.

Para ejecutarlo
```bash
python -m src.tests.test_latency
```