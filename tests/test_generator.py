import os, sys; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from pydantic import ValidationError

from app.schemas.pid import PipingSystem, HandlelisteResponse
from app.services.generator import generate_handleliste


def test_generate_handleliste_valid():
    system = PipingSystem(
        components=["pipe", "valve", "pump", "flange"],
        lines=[
            {"start": 0, "end": 1, "size": "1\""},
            {"start": 1, "end": 2, "size": "1\""},
            {"start": 2, "end": 3, "size": "1\""},
        ],
    )
    response = generate_handleliste(system)
    assert isinstance(response, HandlelisteResponse)
    assert response.items == [
        "Pipe Item",
        "Parker Coupling",
        "Valve Item",
        "Parker Adapter",
        "Pump Item",
        "Parker Connector",
        "Flange Item",
    ]


def test_generate_handleliste_invalid_component():
    with pytest.raises(ValidationError):
        generate_handleliste(PipingSystem(components=["pipe", "unknown"], lines=[]))


def test_generate_handleliste_no_error_on_unlisted_transition():
    system = PipingSystem(
        components=["pump", "filter"],
        lines=[{"start": 0, "end": 1, "size": "1\""}],
    )
    response = generate_handleliste(system)
    # The pump and filter items should still appear even though the transition
    # was not explicitly listed in the fitting table.
    assert response.items[0] == "Pump Item"
    assert response.items[-1] == "Filter Item"


def test_generate_handleliste_with_line_features():
    system = PipingSystem(
        components=["pipe", "valve", "pump"],
        lines=[
            {"start": 0, "end": 1, "size": "1\"", "bulkhead": True},
            {"start": 1, "end": 2, "size": "3/8\""},
        ],
    )
    response = generate_handleliste(system)
    assert "Parker Bulkhead" in response.items
    assert "Parker Adapter" in response.items


def test_generate_handleliste_other_brand():
    system = PipingSystem(
        components=["pipe", "valve"],
        lines=[{"start": 0, "end": 1, "size": "1\""}],
    )
    response = generate_handleliste(system, brand="butech")
    assert response.items[1] == "Butech Coupling"
