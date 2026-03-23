import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import get_settings

client = TestClient(app)
settings = get_settings()

def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["engine"] == settings.engine_version
    assert data["version"] == settings.app_version

def test_docs_endpoint():
    # Test que l'URL /docs renvoie bien le HTML de Scalar
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Scalar" in response.text or "openapi" in response.text

def test_root_not_found():
    # Test qu'une route inexistante renvoie bien 404
    response = client.get("/non-existent")
    assert response.status_code == 404

def test_app_lifespan(caplog):
    # Tester le lifespan (startup/shutdown) via le TestClient en context manager
    with caplog.at_level("INFO"):
        with TestClient(app):
            # Vérifier log de démarrage
            assert any("starting..." in record.message for record in caplog.records)
        
        # Vérifier log d'extinction
        assert any("shutting down" in record.message for record in caplog.records)
