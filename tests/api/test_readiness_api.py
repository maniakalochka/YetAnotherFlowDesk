import pytest
from fastapi.testclient import TestClient

from flowdesk.main import app


@pytest.mark.integration
def test_readiness_uses_test_database_and_broker() -> None:
    with TestClient(app) as client:
        response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
