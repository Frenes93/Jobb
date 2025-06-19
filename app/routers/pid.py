from fastapi import APIRouter

from app.schemas.pid import PipingSystem, HandlelisteResponse
from app.services.generator import generate_handleliste

router = APIRouter(prefix="/pid", tags=["pid"])


@router.post("/handleliste", response_model=HandlelisteResponse)
async def create_handleliste(payload: PipingSystem) -> HandlelisteResponse:
    """Generate a handleliste for the provided piping system."""
    return generate_handleliste(payload)
