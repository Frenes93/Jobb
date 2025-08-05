"""Simple tubing designer GUI using Dear PyGui."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple
import json
from pathlib import Path

import math
import time


try:
    import dearpygui.dearpygui as dpg
except ImportError as e:
    raise ImportError(
        "Dear PyGui is not installed. Please install it using 'pip install dearpygui'."
    ) from e

# ---------------------------------------------------------------------------
# Global state
# ---------------------------------------------------------------------------

PIPING_MODE = False
# Snap-to-geometry flag
SNAP_ENABLED = True

# Line selection helpers
SELECTED_LINE: int | None = None
ENDPOINT_MARKERS: list[int] = []
MIDPOINT_MARKER: int | None = None



# Hover feedback helpers
HOVERED_LINE: int | None = None

# Drag helpers
DRAG_START_POS: Tuple[float, float] | None = None
DRAG_LINE_ORIGINAL: tuple[tuple[float, float], tuple[float, float]] | None = None

# UI label helper
CURRENT_SELECTION: str = "None"




def toggle_piping_mode(sender, app_data):
    """Enable or disable piping mode from UI."""
    global PIPING_MODE
    PIPING_MODE = app_data
    print(f"Piping mode {'enabled' if PIPING_MODE else 'disabled'}")
    update_info_label()


def toggle_snap(sender, app_data):
    """Enable or disable endpoint snapping from UI."""
    global SNAP_ENABLED
    SNAP_ENABLED = app_data
    print(f"Snap {'enabled' if SNAP_ENABLED else 'disabled'}")
    update_info_label()


def toggle_snap(sender, app_data):
    """Enable or disable endpoint snapping from UI."""
    global SNAP_ENABLED
    SNAP_ENABLED = app_data
    print(f"Snap {'enabled' if SNAP_ENABLED else 'disabled'}")


def toggle_snap(sender, app_data):
    """Enable or disable endpoint snapping from UI."""
    global SNAP_ENABLED
    SNAP_ENABLED = app_data
    print(f"Snap {'enabled' if SNAP_ENABLED else 'disabled'}")

# ---------------------------------------------------------------------------
# Interactivity helpers
# ---------------------------------------------------------------------------

selected_item: tuple[int, object] | None = None
"""Currently selected draw tag and bound object."""

interactable_items: dict[int, object] = {}
"""Mapping of draw tags to their backing data objects."""


def update_info_label() -> None:
    """Update the state label on the canvas."""
    mode = "Piping" if PIPING_MODE else "Select"
    snap = "On" if SNAP_ENABLED else "Off"
    text = f"Mode: {mode} | Snap: {snap} | Selection: {CURRENT_SELECTION}"
    if dpg.does_item_exist("info_label"):
        dpg.configure_item("info_label", text=text)



def clear_highlight() -> None:
    """Remove the selection highlight if present."""

    global SELECTED_LINE, ENDPOINT_MARKERS, MIDPOINT_MARKER, CURRENT_SELECTION

    if dpg.does_item_exist("selection_marker"):
        dpg.delete_item("selection_marker")
    if dpg.does_item_exist("highlighted_line"):
        dpg.delete_item("highlighted_line")
    for marker in ENDPOINT_MARKERS:
        if dpg.does_item_exist(marker):
            dpg.delete_item(marker)
    ENDPOINT_MARKERS.clear()
    if MIDPOINT_MARKER is not None and dpg.does_item_exist(MIDPOINT_MARKER):
        dpg.delete_item(MIDPOINT_MARKER)
    MIDPOINT_MARKER = None
    SELECTED_LINE = None
    

    CURRENT_SELECTION = "None"
    highlight_hover_line(None)
    update_info_label()



def highlight_selection(pos: Tuple[float, float]) -> None:
    """Draw a highlight circle around the given position."""
    global CURRENT_SELECTION
    clear_highlight()
    dpg.draw_circle(
        center=pos,
        radius=10,
        color=(255, 255, 0, 255),
        thickness=2,
        parent="ui_layer",
        tag="selection_marker",
    )
    CURRENT_SELECTION = "Component"
    update_info_label()


def register_interactable(tag: int, obj: object) -> None:
    """Register a draw item for interaction."""
    interactable_items[tag] = obj


def move_line_endpoint(line_tag: int, endpoint_idx: int, new_pos: Tuple[float, float]) -> None:
    """Move one endpoint of a drawn line and update the backing object."""
    cfg = dpg.get_item_configuration(line_tag)
    p1, p2 = cfg["p1"], cfg["p2"]
    new_p1 = new_pos if endpoint_idx == 0 else p1
    new_p2 = new_pos if endpoint_idx == 1 else p2
    dpg.configure_item(line_tag, p1=new_p1, p2=new_p2)
    line_obj = interactable_items.get(line_tag)
    if isinstance(line_obj, Tubing):
        line_obj.start = new_p1
        line_obj.end = new_p2


def move_whole_line(line_tag: int, delta: Tuple[float, float]) -> None:
    """Translate a line by the given delta."""
    cfg = dpg.get_item_configuration(line_tag)
    p1, p2 = cfg["p1"], cfg["p2"]
    new_p1 = (p1[0] + delta[0], p1[1] + delta[1])
    new_p2 = (p2[0] + delta[0], p2[1] + delta[1])
    dpg.configure_item(line_tag, p1=new_p1, p2=new_p2)
    line_obj = interactable_items.get(line_tag)
    if isinstance(line_obj, Tubing):
        line_obj.start = new_p1
        line_obj.end = new_p2


def highlight_line(tag: int) -> None:
    """Highlight a tubing line and show draggable markers."""
global SELECTED_LINE, ENDPOINT_MARKERS, MIDPOINT_MARKER, CURRENT_SELECTION
clear_highlight()
highlight_hover_line(None)
    SELECTED_LINE = tag

    cfg = dpg.get_item_configuration(tag)
    p1, p2 = cfg["p1"], cfg["p2"]

    dpg.draw_line(p1=p1, p2=p2, color=(255, 255, 0), thickness=3,

                  parent="drawlist", tag="highlighted_line")

    ENDPOINT_MARKERS = []
    for i, point in enumerate([p1, p2]):
        drag_tag = dpg.draw_circle(
            center=point,
            radius=6,
            color=(0, 255, 255),
            fill=(0, 255, 255),
            parent="drawlist",
        )
        dpg.set_drag_callback(drag_tag, lambda s, a, u=i: on_drag_endpoint(tag, u))
        ENDPOINT_MARKERS.append(drag_tag)

    midpoint = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
    MIDPOINT_MARKER = dpg.draw_rectangle(
        pmin=(midpoint[0] - 5, midpoint[1] - 5),
        pmax=(midpoint[0] + 5, midpoint[1] + 5),
        color=(0, 255, 0),
        fill=(0, 255, 0),
      
parent="ui_layer",
)
dpg.set_drag_callback(MIDPOINT_MARKER, lambda s, a: on_drag_line(tag))
CURRENT_SELECTION = "Line"
update_info_label()



def find_nearest_snap_target(pos: Tuple[float, float], threshold: float = 15) -> Tuple[float, float] | None:
    """Return the position of the nearest snap target within the threshold."""
    candidates: list[Tuple[float, float]] = []
    for _, obj in interactable_items.items():
        if hasattr(obj, "position"):
            candidates.append(obj.position)
    # Include endpoints of existing tubing lines
    for tube in PROJECT.tubings:
        candidates.append(tube.start)
        candidates.append(tube.end)

    nearest: Tuple[float, float] | None = None
    best_dist = threshold
    for c in candidates:
        d = math.dist(pos, c)
        if d <= best_dist:
            nearest = c
            best_dist = d
    return nearest

# Provide visual and snap feedback when dragging an endpoint. Handles color, snap preview, and drag preview rendering.
def on_drag_endpoint(line_tag: int, endpoint_idx: int) -> None:
    """Drag handler for endpoint markers."""
    mouse_pos = dpg.get_mouse_pos(local=False)

    if SNAP_ENABLED:
        snap_target = find_nearest_snap_target(mouse_pos)
        new_pos = snap_target if snap_target else mouse_pos
    else:
snap_target = find_nearest_snap_target(mouse_pos) if SNAP_ENABLED else None
new_pos = snap_target if snap_target else mouse_pos

move_line_endpoint(line_tag, endpoint_idx, new_pos)
highlight_line(line_tag)

color = (0, 255, 0) if snap_target else (255, 165, 0)
if ENDPOINT_MARKERS:
    dpg.configure_item(ENDPOINT_MARKERS[endpoint_idx], color=color, fill=color)

if dpg.does_item_exist("drag_preview"):
    dpg.delete_item("drag_preview")
dpg.draw_line(DRAG_START_POS, new_pos, color=(200, 200, 200), thickness=1,
              parent="ui_layer", tag="drag_preview")

if snap_target:
    if dpg.does_item_exist("snap_effect"):
        dpg.delete_item("snap_effect")
    dpg.draw_circle(center=snap_target, radius=8, color=(0, 0, 255),
                    thickness=2, parent="ui_layer", tag="snap_effect")
else:
    if dpg.does_item_exist("snap_effect"):
        dpg.delete_item("snap_effect")

    mouse_pos = dpg.get_mouse_pos(local=False)
    cfg = dpg.get_item_configuration(line_tag)
    p1, p2 = cfg["p1"], cfg["p2"]
    midpoint = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
if DRAG_LINE_ORIGINAL is None:
    DRAG_LINE_ORIGINAL = (p1, p2)

dx, dy = mouse_pos[0] - midpoint[0], mouse_pos[1] - midpoint[1]
move_whole_line(line_tag, (dx, dy))
highlight_line(line_tag)

# While dragging a tubing line, show a preview of its original position and update its visual highlight and midpoint feedback.
if MIDPOINT_MARKER is not None:
    dpg.configure_item(MIDPOINT_MARKER, color=(255, 165, 0), fill=(255, 165, 0))

if dpg.does_item_exist("drag_preview"):
    dpg.delete_item("drag_preview")

dpg.draw_line(DRAG_LINE_ORIGINAL[0], DRAG_LINE_ORIGINAL[1],
              color=(200, 200, 200), thickness=1,
              parent="ui_layer", tag="drag_preview")



def on_mouse_click(sender, app_data):
    """Handle left-clicks for selection or starting lines."""
    global selected_item
    mouse_pos = dpg.get_mouse_pos(local=False)

    if PIPING_MODE:
        selected_item = None
        clear_highlight()
        highlight_hover_line(None)
        start_line(sender, app_data)
        return


    for tag, obj in interactable_items.items():
        if hasattr(obj, "position"):
            pos = obj.position
            if math.dist(mouse_pos, pos) <= 10:
                selected_item = (tag, obj)
                highlight_selection(pos)

                highlight_hover_line(None)

                return

    for tag, obj in interactable_items.items():
        if isinstance(obj, Tubing):
            if point_near_segment(mouse_pos, obj.start, obj.end, threshold=6.0):
                selected_item = None
                highlight_line(tag)
                highlight_hover_line(None)

                return


    selected_item = None
    clear_highlight()



def on_mouse_drag(sender, app_data):
    """Move the selected item with the mouse."""
    if not selected_item:
        return

    tag, obj = selected_item
    new_pos = dpg.get_mouse_pos(local=False)
    obj.position = new_pos

    if isinstance(obj, Valve):
        dpg.configure_item(tag, pmin=(new_pos[0] - 5, new_pos[1] - 5), pmax=(new_pos[0] + 5, new_pos[1] + 5))
    elif isinstance(obj, Tee):
        dpg.configure_item(tag, center=new_pos)
    elif isinstance(obj, Analyzer):
        dpg.configure_item(
            tag,
            p1=(new_pos[0], new_pos[1] - 5),
            p2=(new_pos[0] - 5, new_pos[1] + 5),
            p3=(new_pos[0] + 5, new_pos[1] + 5),
        )

    highlight_selection(new_pos)


def on_mouse_release(sender, app_data):
    """Finish drawing if not interacting with an item."""
    global DRAG_START_POS, DRAG_LINE_ORIGINAL
    if DRAG_START_POS is not None or DRAG_LINE_ORIGINAL is not None:
        if dpg.does_item_exist("drag_preview"):
            dpg.delete_item("drag_preview")
        if dpg.does_item_exist("snap_effect"):
            dpg.delete_item("snap_effect")
        DRAG_START_POS = None
        DRAG_LINE_ORIGINAL = None
        highlight_line(SELECTED_LINE) if SELECTED_LINE is not None else None
        return
    if selected_item is None:
        finish_line(sender, app_data)



def delete_selected_item() -> None:
    """Delete the currently selected component from the canvas and project."""
    global selected_item, SELECTED_LINE
    if SELECTED_LINE is not None:
        obj = interactable_items.pop(SELECTED_LINE, None)
        if isinstance(obj, Tubing) and obj in PROJECT.tubings:
            PROJECT.tubings.remove(obj)
        if dpg.does_item_exist(SELECTED_LINE):
            dpg.delete_item(SELECTED_LINE)
        clear_highlight()
        SELECTED_LINE = None
        return

    if not selected_item:
        return

    tag, obj = selected_item
    if isinstance(obj, Valve) and obj in PROJECT.valves:
        PROJECT.valves.remove(obj)
    elif isinstance(obj, Tee) and obj in PROJECT.tees:
        PROJECT.tees.remove(obj)
    elif isinstance(obj, Analyzer) and obj in PROJECT.analyzers:
        PROJECT.analyzers.remove(obj)

    dpg.delete_item(tag)
    interactable_items.pop(tag, None)
    clear_highlight()
    selected_item = None


selection_rect_tag = "selection_box"
selection_start_pos: Tuple[float, float] | None = None
rectangle_active = False


def on_right_click_down(sender, app_data) -> None:
    """Begin rectangle selection for bulk delete."""
    global selection_start_pos, rectangle_active
    selection_start_pos = dpg.get_mouse_pos(local=False)
    rectangle_active = True
    if dpg.does_item_exist(selection_rect_tag):
        dpg.delete_item(selection_rect_tag)


def on_right_drag(sender, app_data) -> None:
    """Update the selection rectangle while dragging."""
    if not rectangle_active or selection_start_pos is None:
        return
    mouse_pos = dpg.get_mouse_pos(local=False)
    if dpg.does_item_exist(selection_rect_tag):
        dpg.delete_item(selection_rect_tag)
    dpg.draw_rectangle(
        pmin=selection_start_pos,
        pmax=mouse_pos,
        color=(255, 255, 0),
        thickness=1,
        parent="drawlist",
        tag=selection_rect_tag,
    )


def on_right_release(sender, app_data) -> None:
    """Delete all components inside the selection rectangle."""
    global rectangle_active, selection_start_pos, selected_item, SELECTED_LINE
    if not rectangle_active or selection_start_pos is None:
        return
    rectangle_active = False
    end_pos = dpg.get_mouse_pos(local=False)
    x1, y1 = selection_start_pos
    x2, y2 = end_pos
    xmin, xmax = sorted([x1, x2])
    ymin, ymax = sorted([y1, y2])

    to_delete: list[int] = []
    for tag, obj in list(interactable_items.items()):
        inside = False
        if hasattr(obj, "position"):
            pos = obj.position
            inside = xmin <= pos[0] <= xmax and ymin <= pos[1] <= ymax
        elif isinstance(obj, Tubing):
            s_in = xmin <= obj.start[0] <= xmax and ymin <= obj.start[1] <= ymax
            e_in = xmin <= obj.end[0] <= xmax and ymin <= obj.end[1] <= ymax
            inside = s_in or e_in
        if inside:
            to_delete.append(tag)

    for tag in to_delete:
        obj = interactable_items.pop(tag)
        if isinstance(obj, Valve) and obj in PROJECT.valves:
            PROJECT.valves.remove(obj)
        elif isinstance(obj, Tee) and obj in PROJECT.tees:
            PROJECT.tees.remove(obj)
        elif isinstance(obj, Analyzer) and obj in PROJECT.analyzers:
            PROJECT.analyzers.remove(obj)
        elif isinstance(obj, Tubing) and obj in PROJECT.tubings:
            PROJECT.tubings.remove(obj)
        dpg.delete_item(tag)
        if SELECTED_LINE == tag:
            clear_highlight()
            SELECTED_LINE = None
        if selected_item and selected_item[0] == tag:
            selected_item = None

    if dpg.does_item_exist(selection_rect_tag):
        dpg.delete_item(selection_rect_tag)


class SystemType(Enum):
    """Supported tubing system types."""

    NPT = "NPT"
    BSP = "BSP"
    ALOK = "Alok"
    LP = "LP"
    MP = "MP"
    HP = "HP"



class FittingBrand(Enum):
    """Supported fitting brands."""

    SWAGELOK = "Swagelok"
    PARKER = "Parker"
    BUTECH = "Butech"


@dataclass
class Valve:
    position: Tuple[float, float]
    connector: str = "male"  # default connector type


@dataclass
class Tee:
    position: Tuple[float, float]


@dataclass
class Analyzer:
    position: Tuple[float, float]
    hose_type: str = "flex"



def point_on_segment(point: Tuple[float, float], start: Tuple[float, float], end: Tuple[float, float], eps: float = 1.0) -> bool:
    """Return True if point lies on the line segment defined by start-end."""
    x, y = point
    x1, y1 = start
    x2, y2 = end
    # bounding box check
    if not (min(x1, x2) - eps <= x <= max(x1, x2) + eps and min(y1, y2) - eps <= y <= max(y1, y2) + eps):
        return False
    # cross product should be near zero for colinear points
    cross = abs((x - x1) * (y2 - y1) - (y - y1) * (x2 - x1))
    if cross > eps:
        return False
    return True


def point_near_segment(point: Tuple[float, float], start: Tuple[float, float], end: Tuple[float, float], threshold: float = 5.0) -> bool:
    """Return True if the point is within *threshold* pixels of the segment."""
    x, y = point
    x1, y1 = start
    x2, y2 = end
    if (x1, y1) == (x2, y2):
        return math.dist(point, start) <= threshold
    dx, dy = x2 - x1, y2 - y1
    t = ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    proj = (x1 + t * dx, y1 + t * dy)
    return math.dist(point, proj) <= threshold


def add_tee(position: Tuple[float, float]) -> None:
    """Append a tee if one does not already exist at the given position."""
    for tee in PROJECT.tees:
        if math.dist(tee.position, position) <= 1.0:
            return
    PROJECT.tees.append(Tee(position=position))



@dataclass
class Tubing:
    start: Tuple[float, float]
    end: Tuple[float, float]




@dataclass
class Project:
    system_type: SystemType = SystemType.NPT

    brand: FittingBrand = FittingBrand.PARKER

    tubings: List[Tubing] = field(default_factory=list)
    valves: List[Valve] = field(default_factory=list)
    tees: List[Tee] = field(default_factory=list)
    analyzers: List[Analyzer] = field(default_factory=list)

    def to_json(self, path: Path) -> None:
        data = {
            "system_type": self.system_type.value,

            "brand": self.brand.value,

            "tubings": [t.__dict__ for t in self.tubings],
            "valves": [v.__dict__ for v in self.valves],
            "tees": [t.__dict__ for t in self.tees],
            "analyzers": [a.__dict__ for a in self.analyzers],
        }
        path.write_text(json.dumps(data, indent=2))

    @classmethod
    def from_json(cls, path: Path) -> "Project":
        data = json.loads(path.read_text())

        project = cls(
            system_type=SystemType(data.get("system_type", "NPT")),
            brand=FittingBrand(data.get("brand", "Parker")),
        )
        for t in data.get("tubings", []):
            project.tubings.append(Tubing(tuple(t["start"]), tuple(t["end"])))

        for v in data.get("valves", []):
            project.valves.append(Valve(tuple(v["position"]), connector=v.get("connector", "male")))
        for te in data.get("tees", []):
            project.tees.append(Tee(tuple(te["position"])))
        for a in data.get("analyzers", []):
            project.analyzers.append(Analyzer(tuple(a["position"]), hose_type=a.get("hose_type", "flex")))
        return project


PROJECT = Project()
CURRENT_LINE: List[float] = []  # temporary line while drawing


def set_system_type(sender, app_data, user_data):
    PROJECT.system_type = user_data



def set_brand(sender, app_data, user_data):
    PROJECT.brand = user_data


def save_project():
    path = dpg.get_value("save_path")
    if path:
        PROJECT.to_json(Path(path))


def load_project():
    path = dpg.get_value("load_path")
    if path and Path(path).is_file():
        global PROJECT
        PROJECT = Project.from_json(Path(path))
        redraw_canvas()


def start_line(sender, app_data):
    global CURRENT_LINE
    clear_highlight()
    global selected_item
    selected_item = None
    pos = dpg.get_mouse_pos(local=False)
    CURRENT_LINE = [pos[0], pos[1]]
    update_info_label()


def finish_line(sender, app_data):
    global CURRENT_LINE
    if not CURRENT_LINE:
        return
    pos = dpg.get_mouse_pos(local=False)
    line = Tubing(start=(CURRENT_LINE[0], CURRENT_LINE[1]), end=(pos[0], pos[1]))


    # Check for branching at start and end
    for t in PROJECT.tubings:
        if point_on_segment(line.start, t.start, t.end):
            add_tee(line.start)
        if point_on_segment(line.end, t.start, t.end):
            add_tee(line.end)
        if point_on_segment(t.start, line.start, line.end):
            add_tee(t.start)
        if point_on_segment(t.end, line.start, line.end):
            add_tee(t.end)


    PROJECT.tubings.append(line)
    # animate creation
    steps = 10
    for i in range(1, steps + 1):
        t = i / steps
        inter = (line.start[0] + (line.end[0]-line.start[0]) * t,
                 line.start[1] + (line.end[1]-line.start[1]) * t)
        if dpg.does_item_exist("create_anim"):
            dpg.delete_item("create_anim")
        dpg.draw_line(line.start, inter, color=(200, 0, 0), thickness=2,
                      parent="drawlist", tag="create_anim")
        dpg.render_dearpygui_frame()
        time.sleep(0.01)
    if dpg.does_item_exist("create_anim"):
        dpg.delete_item("create_anim")
    CURRENT_LINE = []
    redraw_canvas()


def add_valve():
    pos = dpg.get_mouse_pos(local=False)
    PROJECT.valves.append(Valve(position=pos))
    redraw_canvas()


def add_analyzer():
    pos = dpg.get_mouse_pos(local=False)
    PROJECT.analyzers.append(Analyzer(position=pos))
    redraw_canvas()


def redraw_canvas():
    dpg.delete_item("drawlist", children_only=True)
    if dpg.does_item_exist("ui_layer"):
        dpg.delete_item("ui_layer", children_only=True)
    interactable_items.clear()
    for idx, line in enumerate(PROJECT.tubings):
        tag = f"tubing_{idx}"
        dpg.draw_line(line.start, line.end, color=(200, 0, 0), thickness=2, parent="drawlist", tag=tag)
        register_interactable(tag, line)

    for tee in PROJECT.tees:
        tag = dpg.draw_circle(tee.position, 5, color=(0, 0, 200), fill=(0, 0, 200), parent="drawlist")
        register_interactable(tag, tee)

    for valve in PROJECT.valves:
        tag = dpg.draw_rectangle(
            (valve.position[0] - 5, valve.position[1] - 5),
            (valve.position[0] + 5, valve.position[1] + 5),
            color=(0, 200, 0),
            fill=(0, 200, 0),
            parent="drawlist",
        )
        register_interactable(tag, valve)
    for analyzer in PROJECT.analyzers:
        tag = dpg.draw_triangle(
            (analyzer.position[0], analyzer.position[1] - 5),
            (analyzer.position[0] - 5, analyzer.position[1] + 5),
            (analyzer.position[0] + 5, analyzer.position[1] + 5),
            color=(200, 200, 0),
            fill=(200, 200, 0),
            parent="drawlist",
        )
        register_interactable(tag, analyzer)

    if selected_item:
        _, obj = selected_item
        highlight_selection(obj.position)

    if SELECTED_LINE is not None and dpg.does_item_exist(SELECTED_LINE):
        highlight_line(SELECTED_LINE)

# Ensure info label reflects current interaction state (mode, selection, snapping)
    update_info_label()


def main():
    dpg.create_context()
    dpg.create_viewport(title="Tubing Designer", width=800, height=600)
    
    with dpg.window(label="Controls", width=200, height=600, pos=(0, 0)):
        dpg.add_text("System Type")
        for st in SystemType:
            dpg.add_button(label=st.value, callback=set_system_type, user_data=st)
        dpg.add_separator()
        dpg.add_text("Fitting Brand")
        for br in FittingBrand:
            dpg.add_button(label=br.value, callback=set_brand, user_data=br)
        dpg.add_separator()
        dpg.add_button(label="Add Valve", callback=lambda: add_valve())
        dpg.add_button(label="Add Analyzer", callback=lambda: add_analyzer())
        dpg.add_checkbox(label="Piping Mode", callback=toggle_piping_mode, default_value=False)
        dpg.add_checkbox(label="Snap Geometry", callback=toggle_snap, default_value=True)
        dpg.add_button(label="Delete Selected", callback=lambda: delete_selected_item())
        dpg.add_input_text(label="Save Path", tag="save_path")
        dpg.add_button(label="Save", callback=lambda: save_project())
        dpg.add_input_text(label="Load Path", tag="load_path")
        dpg.add_button(label="Load", callback=lambda: load_project())

    with dpg.window(label="Canvas", tag="Canvas", width=600, height=600, pos=(200, 0)):
        with dpg.drawlist(width=580, height=580, tag="drawlist"):
            pass
        with dpg.drawlist(width=580, height=580, tag="ui_layer"):
            dpg.draw_text((10, 560), "", tag="info_label")

    with dpg.handler_registry():
        dpg.add_mouse_click_handler(button=dpg.mvMouseButton_Left, callback=on_mouse_click)
        dpg.add_mouse_drag_handler(button=dpg.mvMouseButton_Left, callback=on_mouse_drag)
        dpg.add_mouse_release_handler(button=dpg.mvMouseButton_Left, callback=on_mouse_release)
        dpg.add_mouse_move_handler(callback=on_mouse_move)
        dpg.add_mouse_click_handler(button=dpg.mvMouseButton_Right, callback=on_right_click_down)
        dpg.add_mouse_drag_handler(button=dpg.mvMouseButton_Right, callback=on_right_drag)
        dpg.add_mouse_release_handler(button=dpg.mvMouseButton_Right, callback=on_right_release)


    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("Canvas", True)
    update_info_label()
    while dpg.is_dearpygui_running():
        dpg.render_dearpygui_frame()
    dpg.destroy_context()


if __name__ == "__main__":
    main()
