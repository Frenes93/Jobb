from fastapi import APIRouter
from app.schemas.pid import PipingSystem, HandlelisteResponse
from app.services.generator import generate_handleliste

router = APIRouter(
