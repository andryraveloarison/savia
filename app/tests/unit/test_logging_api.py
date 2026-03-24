import pytest
import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_correlation_id_propagation():
    # Test que le Correlation ID est généré et retourné dans les headers
    response = client.post(
        "/tickets/analyze",
        json={
            "ticket_id": "LOG-1",
            "message": "Test logging",
            "attachments": [],
            "customer": {"id": "C-1", "name": "John"},
            "equipment": {"type": "boiler", "model": "V-100"},
            "history": {"previous_tickets": 0}
        }
    )
    assert response.status_code == 200
    assert "X-Correlation-ID" in response.headers
    correlation_id = response.headers["X-Correlation-ID"]
    assert len(correlation_id) > 0

def test_custom_correlation_id():
    # Test qu'on peut passer notre propre Correlation ID
    custom_id = "my-custom-id-123"
    response = client.post(
        "/tickets/analyze",
        json={
            "ticket_id": "LOG-2",
            "message": "Test logging custom",
            "attachments": [],
            "customer": {"id": "C-1", "name": "John"},
            "equipment": {"type": "boiler", "model": "V-100"},
            "history": {"previous_tickets": 0}
        },
        headers={"X-Correlation-ID": custom_id}
    )
    assert response.status_code == 200
    assert response.headers["X-Correlation-ID"] == custom_id

def test_custom_json_formatter_with_levelname():
    """log_record contient levelname → level = levelname.upper()"""
    from app.core.logging import CustomJsonFormatter
    import logging
    from unittest.mock import patch

    formatter = CustomJsonFormatter()
    record = logging.LogRecord(
        name="savia", level=logging.WARNING,
        pathname="", lineno=0, msg="test", args=(), exc_info=None
    )

    log_record = {"levelname": "warning"}  # présent mais en minuscule
    formatter.add_fields(log_record, record, {})

    assert log_record["level"] == "WARNING"
