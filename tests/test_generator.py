import os, sys; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from pydantic import ValidationError

from app.schemas.pid import PipingSystem, HandlelisteResponse
from app.services.generator import generate_handleliste


def test_generate_handleliste_valid():
    system = PipingSystem(components=["pipe", "valve", "pump", "flange"])
    response = generate_handleliste(system)
    assert isinstance(response, HandlelisteResponse)
    assert response.items == [
        "Pipe Item",
        "Valve Item",
        "Pump Item",
        "Flange Item",
    ]


def test_generate_handleliste_invalid_component():
    with pytest.raises(ValidationError):
        generate_handleliste(PipingSystem(components=["pipe", "unknown"]))


def test_generate_handleliste_invalid_transition():
    system = PipingSystem(components=["pump", "pipe"])
    with pytest.raises(ValueError):
        generate_handleliste(system)
