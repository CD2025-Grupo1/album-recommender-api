# Instalación y Configuración del Entorno

Sigue estos pasos para levantar el proyecto en tu máquina local.

## Prerrequisitos
- Tener Python 3.9 o superior instalado.
- Tener PostgreSQL instalado y corriendo.

## Paso a Paso

### 1. Crear Entorno Virtual
python -m venv venv

### 2. Activar Entorno Virtual
.\venv\Scripts\activate

### 3. Instalar Dependencias
pip install --upgrade pip
pip install -r requirements.txt

### 4. Configurar Variables de Entorno
Crear un archivo llamado .env en la raíz del proyecto (junto a este README) y define tus credenciales locales. No subas este archivo al repositorio.

Ejemplo de contenido:
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nombre_de_tu_bd
DB_USER=postgres
DB_PASSWORD=tu_contraseña

### 5. Ejecutar Aplicación (siempre dentro del entorno)
python -m src.app