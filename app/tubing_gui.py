"""Simple tubing designer GUI using Dear PyGui."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple
import json
from pathlib import Path

import math


from dearpygui import dearpygui as dpg


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
    pos = dpg.get_mouse_pos(local=False)
    CURRENT_LINE = [pos[0], pos[1]]


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
    for line in PROJECT.tubings:
        dpg.draw_line(line.start, line.end, color=(200, 0, 0), thickness=2, parent="drawlist")

    for tee in PROJECT.tees:
        dpg.draw_circle(tee.position, 5, color=(0, 0, 200), fill=(0, 0, 200), parent="drawlist")

    for valve in PROJECT.valves:
        dpg.draw_rectangle((valve.position[0]-5, valve.position[1]-5), (valve.position[0]+5, valve.position[1]+5),
                           color=(0, 200, 0), fill=(0, 200, 0), parent="drawlist")
    for analyzer in PROJECT.analyzers:
        dpg.draw_triangle((analyzer.position[0], analyzer.position[1]-5),
                          (analyzer.position[0]-5, analyzer.position[1]+5),
                          (analyzer.position[0]+5, analyzer.position[1]+5),
                          color=(200, 200, 0), fill=(200, 200, 0), parent="drawlist")


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
        dpg.add_input_text(label="Save Path", tag="save_path")
        dpg.add_button(label="Save", callback=lambda: save_project())
        dpg.add_input_text(label="Load Path", tag="load_path")
        dpg.add_button(label="Load", callback=lambda: load_project())

    with dpg.window(label="Canvas", tag="Canvas", width=600, height=600, pos=(200, 0)):
        with dpg.drawlist(width=580, height=580, tag="drawlist"):
            pass

    with dpg.handler_registry():
        dpg.add_mouse_click_handler(button=dpg.mvMouseButton_Left, callback=start_line)
        dpg.add_mouse_release_handler(button=dpg.mvMouseButton_Left, callback=finish_line)


    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("Canvas", True)
    while dpg.is_dearpygui_running():
        dpg.render_dearpygui_frame()
    dpg.destroy_context()


if __name__ == "__main__":
    main()
