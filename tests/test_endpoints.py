import os, sys; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import asyncio
import pytest
from pydantic import ValidationError

from app.main import frontend, read_root
from app.routers.pid import handleliste
from app.schemas.pid import PipingSystem
from fastapi import HTTPException


def test_frontend_returns_message():
    response = asyncio.run(frontend())
    assert response == {"message": "Welcome to the Jobb API"}


def test_api_root_endpoint():
    response = asyncio.run(read_root())
    assert response == {"message": "Welcome to the Jobb FastAPI Example"}


def test_handleliste_endpoint_valid():
    system = PipingSystem(
        components=["pipe", "valve", "pump", "flange"],
        lines=[
            {"start": 0, "end": 1, "size": "1\""},
            {"start": 1, "end": 2, "size": "1\""},
            {"start": 2, "end": 3, "size": "1\""},
        ],
    )
    response = asyncio.run(handleliste(system))
    assert response.items == [
        "Pipe Item",
        "Parker Coupling",
        "Valve Item",
        "Parker Adapter",
        "Pump Item",
        "Parker Connector",
        "Flange Item",
    ]


def test_handleliste_endpoint_allows_any_transition():
    system = PipingSystem(
        components=["pump", "filter"],
        lines=[{"start": 0, "end": 1, "size": "1\""}],
    )
    response = asyncio.run(handleliste(system))
    assert response.items[0] == "Pump Item"
    assert response.items[-1] == "Filter Item"


def test_handleliste_endpoint_brand_param():
    system = PipingSystem(
        components=["pipe", "valve"],
        lines=[{"start": 0, "end": 1, "size": "1\""}],
    )
    response = asyncio.run(handleliste(system, brand="swagelok"))
    assert response.items[1] == "Swagelok Coupling"


def test_handleliste_endpoint_invalid_transition():
    system = PipingSystem(
        components=["pump", "pipe"],
        lines=[{"start": 0, "end": 1, "size": "1\""}],
    )
    response = asyncio.run(handleliste(system))
    assert response.items[0] == "Pump Item"


def test_handleliste_endpoint_with_line_features():
    system = PipingSystem(
        components=["pipe", "valve", "pump"],
        lines=[
            {"start": 0, "end": 1, "size": "1\"", "tee": True},
            {"start": 1, "end": 2, "size": "3/8\""},
        ],
    )
    response = asyncio.run(handleliste(system))
    assert "Parker Tee" in response.items
    assert "Parker Adapter" in response.items
