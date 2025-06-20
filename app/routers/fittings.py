from fastapi import APIRouter, HTTPException

from app.schemas.fittings import Fitting
from app.services.fittings_store import get_fitting, add_fitting

router = APIRouter(prefix="/fittings", tags=["fittings"])


@router.get("/{code}", response_model=Fitting)
async def read_fitting(code: str) -> Fitting:
    """Retrieve information about a fitting by its code."""
    fitting = get_fitting(code)
    if not fitting:
        raise HTTPException(status_code=404, detail="Fitting not found")
    return fitting


@router.post("/", status_code=201, response_model=Fitting)
async def create_fitting(fitting: Fitting) -> Fitting:
    """Add a new fitting to the store."""
    add_fitting(fitting)
    return fitting
