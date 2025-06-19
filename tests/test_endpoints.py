import os, sys; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import asyncio
import pytest
from pydantic import ValidationError

from app.main import frontend, read_root
from app.routers.pid import handleliste
from app.schemas.pid import PipingSystem
from fastapi.responses import FileResponse
from fastapi import HTTPException


def test_frontend_served():
    response = asyncio.run(frontend())
    assert isinstance(response, FileResponse)


def test_api_root_endpoint():
    response = asyncio.run(read_root())
    assert response == {"message": "Welcome to the Jobb FastAPI Example"}


def test_handleliste_endpoint_valid():
    system = PipingSystem(components=["pipe", "valve", "pump", "flange"])
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


def test_handleliste_endpoint_invalid_component():
    with pytest.raises(ValidationError):
        PipingSystem(components=["pipe", "unknown"])


def test_handleliste_endpoint_invalid_transition():
    system = PipingSystem(components=["pump", "pipe"])
    with pytest.raises(HTTPException):
        asyncio.run(handleliste(system))
