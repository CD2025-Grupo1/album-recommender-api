# Instalación y Configuración del Entorno

Sigue estos pasos para levantar el proyecto en tu máquina local.

## Prerrequisitos
- Tener Python 3.9 o superior instalado.
- Tener PostgreSQL instalado y corriendo.

## Ejecutar Aplicación - Paso a Paso

### 1. Crear Entorno Virtual
```bash
python -m venv venv
```

### 2. Activar Entorno Virtual
```bash
.\venv\Scripts\activate
```

### 3. Instalar Dependencias
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
Crear un archivo llamado .env en la raíz del proyecto (junto a este README) y define tus credenciales locales. No subas este archivo al repositorio.

Ejemplo de contenido:
```bash
DB_HOST=localhost
DB_PORT=5433 # generalmente se usa 5432
DB_NAME=CD_TPI
DB_USER=postgres
DB_PASSWORD=admin
```

### 5. Configuración de la Base de Datos
El sistema requiere una base de datos poblada.

* Crear la BD: accede a tu gestor de base de datos y crea una base vacía con el nombre que definiste en el paso anterior (ej: CD_TPI)

```sql
CREATE DATABASE "CD_TPI";
```

* Probar la BD: ejecuta el script SQL de inicialización que se encuentra en archivo init_db.sql 

### 6. Ejecutar Aplicación (siempre dentro del entorno)
```bash
python -m src.app
```

Una vez iniciado:
* API: http://127.0.0.1:8000
* Swagger: http://127.0.0.1:8000/docs