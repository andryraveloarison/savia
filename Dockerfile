FROM python:3.12-slim

# Métadonnées
LABEL maintainer="Dataven Technologies"
LABEL description="Savia — Moteur d'aide à la décision SAV"

# Répertoire de travail
WORKDIR /savia

# Copier les dépendances en premier (cache Docker optimisé)
COPY requirements.txt .

# Installer les dépendances + pytest + coverage + allure + httpx
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install pytest pytest-cov allure-pytest httpx

# Copier le code applicatif
COPY app/ ./app/
COPY .env.example .env

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/savia

# Port exposé
EXPOSE 8000

# Lancement par défaut
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]