# ==========================================
# Dockerfile - Backend FastAPI
# Smart Campus Virtual - UNGE
# ==========================================

# Imagen base oficial de Python 3.12 (versión slim = ligera)
FROM python:3.12-slim

# Metadatos
LABEL maintainer="Tu Nombre <tu@email.com>"
LABEL description="Backend FastAPI - Smart Campus Virtual UNGE"

# Variables de entorno de Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar requirements primero (mejor caché de Docker)
COPY backend/requirements.txt .
RUN pip install --upgrade pip --timeout 300 --retries 20 && \
    pip install -r requirements.txt --timeout 300 --retries 20

# Copiar el resto del código del backend
COPY backend/ .

# Exponer puerto
EXPOSE 8000

# Comando por defecto (se sobrescribe en docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]