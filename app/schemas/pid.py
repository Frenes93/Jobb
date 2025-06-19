from pydantic import BaseModel


class PipingSystem(BaseModel):
    name: str
    length: float


class HandlelisteResponse(BaseModel):
    handleliste: str
