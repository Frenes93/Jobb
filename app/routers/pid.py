from fastapi import APIRouter, HTTPException
from app.schemas.pid import PipingSystem, HandlelisteResponse
from app.services.generator import generate_handleliste

router = APIRouter(prefix="/pid", tags=["pid"])

@router.post("/handleliste", response_model=HandlelisteResponse)
async def handleliste(system: PipingSystem, brand: str = "parker") -> HandlelisteResponse:
    """Generate a handleliste for the provided piping system."""
    try:
        return generate_handleliste(system, brand=brand)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
