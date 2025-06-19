from app.schemas.pid import PipingSystem, HandlelisteResponse


def generate_handleliste(system: PipingSystem) -> HandlelisteResponse:
    """Generate a handleliste for the given piping system."""
    return HandlelisteResponse(items=system.components)
