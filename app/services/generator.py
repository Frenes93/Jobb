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

FITTINGS_BASE = {
    (Component.PIPE, Component.VALVE): "Coupling",
    (Component.VALVE, Component.PUMP): "Adapter",
    (Component.PUMP, Component.FLANGE): "Connector",
    (Component.FLANGE, Component.PIPE): "Gasket",
    (Component.PIPE, Component.FILTER): "Coupling",
    (Component.FILTER, Component.ANALYZER): "Connector",
    (Component.ANALYZER, Component.FLANGE): "Adapter",
}

BRANDS = {"parker", "butech", "swagelok"}

# Allow any component transitions; fittings will be looked up when available


def generate_handleliste(system: PipingSystem, brand: str = "parker") -> HandlelisteResponse:
    """Generate a handleliste for the given piping system.

    Parameters
    ----------
    system:
        The piping system description.
    brand:
        Brand name for fittings (``"parker"``, ``"butech"`` or ``"swagelok"``).
    """

    brand_lc = brand.lower()
    if brand_lc not in BRANDS:
        raise ValueError(f"Unknown brand: {brand}")

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

        # adapter if component already connected with different size
        prev_size = connection_sizes.get(line.start)
        if prev_size is not None and prev_size != line.size:
            items.append(f"{brand_lc.capitalize()} Adapter")

        fitting_base = FITTINGS_BASE.get((start_comp, end_comp))
        if fitting_base:
            items.append(f"{brand_lc.capitalize()} {fitting_base}")

        if line.bulkhead:
            items.append(f"{brand_lc.capitalize()} Bulkhead")
        if line.tee:
            items.append(f"{brand_lc.capitalize()} Tee")

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
