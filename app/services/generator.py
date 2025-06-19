from __future__ import annotations

from app.schemas.pid import Component, PipingSystem, HandlelisteResponse


CATALOG = {
    Component.PIPE: "Pipe Item",
    Component.VALVE: "Valve Item",
    Component.PUMP: "Pump Item",
    Component.FLANGE: "Flange Item",
    Component.FILTER: "Filter Item",
    Component.ANALYZER: "Analyzer Item",
}

FITTINGS = {
    (Component.PIPE, Component.VALVE): "Parker Coupling",
    (Component.VALVE, Component.PUMP): "Parker Adapter",
    (Component.PUMP, Component.FLANGE): "Parker Connector",
    (Component.FLANGE, Component.PIPE): "Parker Gasket",
    (Component.PIPE, Component.FILTER): "Parker Coupling",
    (Component.FILTER, Component.ANALYZER): "Parker Connector",
    (Component.ANALYZER, Component.FLANGE): "Parker Adapter",
}

TRANSITIONS = {
    Component.PIPE: {Component.VALVE, Component.FLANGE, Component.FILTER},
    Component.VALVE: {Component.PUMP, Component.FILTER},
    Component.PUMP: {Component.FLANGE},
    Component.FLANGE: {Component.PIPE},
    Component.FILTER: {Component.ANALYZER},
    Component.ANALYZER: {Component.FLANGE},
}


def generate_handleliste(system: PipingSystem) -> HandlelisteResponse:
    """Generate a handleliste for the given piping system."""

    items: list[str] = []

    for comp in system.components:
        if comp not in CATALOG:
            raise ValueError(f"Unknown component: {comp.value}")

    seen: set[int] = set()
    connection_sizes: dict[int, str] = {}

    for idx, line in enumerate(system.lines):
        try:
            start_comp = system.components[line.start]
            end_comp = system.components[line.end]
        except IndexError as exc:
            raise ValueError("Line references invalid component index") from exc

        # add start component if not added yet
        if line.start not in seen:
            items.append(CATALOG[start_comp])
            seen.add(line.start)

        # check transition validity
        allowed = TRANSITIONS.get(start_comp, set())
        if end_comp not in allowed:
            raise ValueError(
                f"Invalid transition from {start_comp.value} to {end_comp.value}"
            )

        # adapter if component already connected with different size
        prev_size = connection_sizes.get(line.start)
        if prev_size is not None and prev_size != line.size:
            items.append("Parker Adapter")

        fitting = FITTINGS.get((start_comp, end_comp))
        if fitting:
            items.append(fitting)

        if line.bulkhead:
            items.append("Parker Bulkhead")
        if line.tee:
            items.append("Parker Tee")

        connection_sizes[line.start] = line.size
        connection_sizes[line.end] = line.size

        if line.end not in seen:
            items.append(CATALOG[end_comp])
            seen.add(line.end)

    # include standalone components with no lines
    for idx, comp in enumerate(system.components):
        if idx not in seen:
            items.append(CATALOG[comp])

    return HandlelisteResponse(items=items)
