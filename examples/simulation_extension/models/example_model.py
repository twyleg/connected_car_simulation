from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, Optional

from connected_car_simulation.simulation.models.base import (
    SimulationModel,
    SimulationModelFactory,
    SimulationStepContext,
)
from connected_car_simulation.simulation.route import Route


FILE_DIR = Path(__file__).parent
RESOURCES_DIR = FILE_DIR / "resources"


class ExampleModel(SimulationModel):

    TOGGLE_PERIOD_SECONDS = 2.0

    def __init__(self, identifier: int, position_on_route: float):
        self.identifier = identifier
        self.position_on_route = position_on_route
        self.value = False
        self.last_toggle_timestamp = 0.0

    @property
    def model_id(self) -> str:
        return f"example_model_{self.identifier}"

    @property
    def model_type(self) -> str:
        return "example_models"

    @property
    def display_name(self) -> str:
        return f"Example Model {self.identifier}"

    def update(self, context: SimulationStepContext) -> None:
        if (context.simulation_timestamp - self.last_toggle_timestamp) < self.TOGGLE_PERIOD_SECONDS:
            return

        self.value = not self.value
        self.last_toggle_timestamp = context.simulation_timestamp

    def get_state(self) -> Dict[str, Any]:
        return {
            "id": self.identifier,
            "value": self.value,
            "position_on_route": self.position_on_route,
        }

    def get_vehicle_input(self) -> Dict[str, Any]:
        return self.get_state()

    def get_position_on_route(self) -> Optional[float]:
        return self.position_on_route

    def html_overview(self) -> str:
        resource_path = RESOURCES_DIR / "overview.html"
        return resource_path.read_text(encoding="utf-8")

    def html_indicator(self) -> str:
        resource_path = RESOURCES_DIR / "indicator.html"
        return resource_path.read_text(encoding="utf-8")

    def html_tooltip(self) -> str:
        resource_path = RESOURCES_DIR / "tooltip.html"
        return resource_path.read_text(encoding="utf-8")

    def css_styles(self) -> str:
        resource_path = RESOURCES_DIR / "style.css"
        return resource_path.read_text(encoding="utf-8")

    def script_module(self) -> str:
        resource_path = RESOURCES_DIR / "script.js"
        return resource_path.read_text(encoding="utf-8")


class ExampleModelFactory(SimulationModelFactory):

    def create(self, config: Dict[str, Any], route: Route) -> Optional[ExampleModel]:
        identifier = int(config.attrib["id"])
        position_on_route = float(config.attrib["position_on_route"])
        return ExampleModel(identifier, position_on_route)
