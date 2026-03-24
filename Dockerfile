FROM python:3.12-slim

# Métadonnées
LABEL maintainer="Dataven Technologies"
LABEL description="Savia — Moteur d'aide à la décision SAV"

# Créer un utilisateur non-root
RUN useradd --create-home --shell /bin/bash saviauser

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

# Changer l'utilisateur courant pour éviter d’exécuter en root
USER saviauser

# Port exposé
EXPOSE 8000

# Lancement par défaut
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]