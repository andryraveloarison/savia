#!/bin/sh
# run_tests.sh - lancer tests pytest + Allure

echo "🧪 Lancement des tests avec coverage et allure..."
docker compose -f docker-compose.test.yml down --remove-orphans
docker compose -f docker-compose.test.yml run --rm tests

echo "📊 Lancement du serveur Allure..."
docker compose -f docker-compose.test.yml up -d allure

echo "✅ Tests terminés. Ouvre http://localhost:5050 pour voir le rapport Allure"