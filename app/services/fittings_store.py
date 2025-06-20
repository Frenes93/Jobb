"""Simple in-memory store for instrumentation fittings."""
from __future__ import annotations

from typing import Dict, Optional

from app.schemas.fittings import Fitting


_FITTINGS: Dict[str, Fitting] = {
    "4A-C4L-25-SS": Fitting(
        code="4A-C4L-25-SS",
        description="Check valve",
        series="4A",
        configuration="C4L",
        cracking_pressure="25 psi",
        material="stainless steel",
    )
}


def get_fitting(code: str) -> Optional[Fitting]:
    """Return fitting information for the given code."""
    return _FITTINGS.get(code)


def add_fitting(fitting: Fitting) -> None:
    """Add or update a fitting in the store."""
    _FITTINGS[fitting.code] = fitting
