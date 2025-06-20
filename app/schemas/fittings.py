from pydantic import BaseModel


class Fitting(BaseModel):
    """Description of an instrumentation fitting."""

    code: str
    description: str
    series: str
    configuration: str
    cracking_pressure: str | None = None
    material: str | None = None
