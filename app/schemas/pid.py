from typing import List
from pydantic import BaseModel

class PipingSystem(BaseModel):
    """Simple representation of a piping system."""
    components: List[str]

class HandlelisteResponse(BaseModel):
    """Response model for handleliste generation."""
    items: List[str]
