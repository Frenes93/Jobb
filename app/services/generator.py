from __future__ import annotations

from app.schemas.pid import Component, PipingSystem, HandlelisteResponse


CATALOG = {
    Component.PIPE: "Pipe Item",
    Component.VALVE: "Valve Item",
    Component.PUMP: "Pump Item",
    Component.FLANGE: "Flange Item",
}

FITTINGS = {
    (Component.PIPE, Component.VALVE): "Parker Coupling",
    (Component.VALVE, Component.PUMP): "Parker Adapter",
    (Component.PUMP, Component.FLANGE): "Parker Connector",
    (Component.FLANGE, Component.PIPE): "Parker Gasket",
}

TRANSITIONS = {
    Component.PIPE: {Component.VALVE, Component.FLANGE},
    Component.VALVE: {Component.PUMP},
    Component.PUMP: {Component.FLANGE},
    Component.FLANGE: {Component.PIPE},
}


def generate_handleliste(system: PipingSystem) -> HandlelisteResponse:
    """Generate a handleliste for the given piping system."""

    items: list[str] = []
    previous: Component | None = None

    for component in system.components:
        if component not in CATALOG:
            raise ValueError(f"Unknown component: {component.value}")

        if previous is not None:
            allowed = TRANSITIONS.get(previous, set())
            if component not in allowed:
                raise ValueError(
                    f"Invalid transition from {previous.value} to {component.value}"
                )
            fitting = FITTINGS.get((previous, component))
            if fitting:
                items.append(fitting)

        items.append(CATALOG[component])
        previous = component

    return HandlelisteResponse(items=items)
