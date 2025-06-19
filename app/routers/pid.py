from fastapi import APIRouter


router = APIRouter()


@router.get("/ping")
async def ping() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok"}
