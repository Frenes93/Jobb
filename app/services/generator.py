from app.schemas.pid import PipingSystem, HandlelisteResponse


CATALOG = {
    "pipe": "Pipe Item",
    "valve": "Valve Item",
    "pump": "Pump Item",
    "flange": "Flange Item",
}

TRANSITIONS = {
    "pipe": ["valve", "flange"],
    "valve": ["pump"],
    "pump": ["flange"],
    "flange": ["pipe"],
}


def generate_handleliste(system: PipingSystem) -> HandlelisteResponse:
    """Generate a handleliste for the given piping system."""

    items = []
    previous = None
    for component in system.components:
        if component not in CATALOG:
            raise ValueError(f"Unknown component: {component}")

        if previous is not None:
            allowed = TRANSITIONS.get(previous, [])
            if component not in allowed:
                raise ValueError(
                    f"Invalid transition from {previous} to {component}"
                )

        items.append(CATALOG[component])
        previous = component

    return HandlelisteResponse(items=items)
