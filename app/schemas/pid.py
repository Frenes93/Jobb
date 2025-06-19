from __future__ import annotations

from enum import Enum
from typing import List
from pydantic import BaseModel


class Component(str, Enum):
    """Valid components allowed in a ``PipingSystem``."""

    PIPE = "pipe"
    VALVE = "valve"
    PUMP = "pump"
    FLANGE = "flange"

class PipingSystem(BaseModel):
    """Simple representation of a piping system."""

    components: List[Component]

class HandlelisteResponse(BaseModel):
    """Response model for handleliste generation."""

    items: List[str]
