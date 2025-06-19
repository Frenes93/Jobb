from app.schemas.pid import PipingSystem, HandlelisteResponse


def generate_handleliste(system: PipingSystem) -> HandlelisteResponse:
    """Generate a simple handleliste for the given piping system."""
    message = f"Generated handleliste for {system.name} with length {system.length}m"
    return HandlelisteResponse(handleliste=message)
