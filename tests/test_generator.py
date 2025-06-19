import os, sys; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.schemas.pid import PipingSystem, HandlelisteResponse
from app.services.generator import generate_handleliste


def test_generate_handleliste():
    system = PipingSystem(components=["pipe", "valve"])
    response = generate_handleliste(system)
    assert isinstance(response, HandlelisteResponse)
    assert response.items == ["pipe", "valve"]
