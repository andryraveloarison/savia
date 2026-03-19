#!/bin/sh
# run_app.sh - Démarrer l'application Savia

echo "🏗️ Construction et démarrage de Savia..."
docker compose build
docker compose up -d

echo "✅ Savia est prêt !"
echo "📍 API : http://localhost:8000"
echo "📍 Docs : http://localhost:8000/docs"
docker compose logs -f