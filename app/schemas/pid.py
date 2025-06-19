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
    FILTER = "filter"
    ANALYZER = "analyzer"


class Line(BaseModel):
    """Connection between two components."""

    start: int
    end: int
    size: str
    tee: bool = False
    bulkhead: bool = False

class PipingSystem(BaseModel):
    """Simple representation of a piping system."""

    components: List[Component]
    lines: List[Line] = []

class HandlelisteResponse(BaseModel):
    """Response model for handleliste generation."""

    items: List[str]
