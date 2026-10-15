# Smart Campus Virtual

> Plataforma inteligente de gestión universitaria para la UNGE
> Trabajo de Fin de Grado — Informática de Gestión

## 🎯 Descripción

Prototipo funcional de una plataforma web y móvil que centraliza los procesos académicos y administrativos de la Universidad Nacional de Guinea Ecuatorial.

## 🛠️ Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.12 + FastAPI |
| Base de datos | PostgreSQL 16 |
| Frontend | React + Vite + TypeScript |
| IA | scikit-learn |
| Contenedores | Docker + docker-compose |

## 🚀 Inicio rápido

### Requisitos
- Docker
- Docker Compose
- Git

### Pasos

```bash
# 1. Clonar
git clone <url-del-repo>
cd smart-campus-virtual

# 2. Copiar variables de entorno
cp .env.example .env
cp backend/.env.example backend/.env

# 3. Levantar servicios
docker-compose up -d

# 4. Ver logs
docker-compose logs -f backend