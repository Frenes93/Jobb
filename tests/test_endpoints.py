import os, sys; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_handleliste_endpoint_valid():
    payload = {"components": ["pipe", "valve", "pump", "flange"]}
    response = client.post("/pid/handleliste", json=payload)
    assert response.status_code == 200
    assert response.json() == {
        "items": ["Pipe Item", "Valve Item", "Pump Item", "Flange Item"]
    }


def test_handleliste_endpoint_invalid_component():
    payload = {"components": ["pipe", "unknown"]}
    response = client.post("/pid/handleliste", json=payload)
    assert response.status_code == 400


def test_handleliste_endpoint_invalid_transition():
    payload = {"components": ["pump", "pipe"]}
    response = client.post("/pid/handleliste", json=payload)
    assert response.status_code == 400
