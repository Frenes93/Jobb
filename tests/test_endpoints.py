import os, sys; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fastapi.testclient import TestClient
from app.main import app


def test_handleliste_endpoint():
    client = TestClient(app)
    payload = {"components": ["pump", "flange"]}
    response = client.post("/pid/handleliste", json=payload)
    assert response.status_code == 200
    assert response.json() == {"items": ["pump", "flange"]}
