from __future__ import annotations

from enum import Enum
from pathlib import Path
from random import randint
from typing import Any, Dict, Optional

from connected_car_simulation.simulation.models.base import (
    SimulationModel,
    SimulationModelFactory,
    SimulationStepContext,
)
from connected_car_simulation.simulation.route import Route


FILE_DIR = Path(__file__).parent
RESOURCES_DIR = FILE_DIR / "resources" / "traffic_lights"


class TrafficLightState(Enum):
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"


class TrafficLightModel(SimulationModel):

    YELLOW_PERIOD_LENGTH = 1

    def __init__(self, identifier: int, position_on_route: float, lon: float, lat: float, period: float, ratio: float):
        self.identifier = identifier
        self.position_on_route = position_on_route
        self.lon = lon
        self.lat = lat
        self.period = period
        self.ratio = ratio
        self.state = TrafficLightState.RED.value
        self.offset = randint(0, int(period))
        self.t = 0.0

    @property
    def model_id(self) -> str:
        return f"traffic_light_{self.identifier}"

    @property
    def model_type(self) -> str:
        return "traffic_lights"

    @property
    def display_name(self) -> str:
        return f"Traffic Light {self.identifier}"

    def update(self, context: SimulationStepContext) -> None:
        self.t = (context.simulation_timestamp + self.offset) % self.period
        red_period_length = self.period * self.ratio
        if self.t < red_period_length:
            self.state = TrafficLightState.RED.value
        elif self.t < (red_period_length + self.YELLOW_PERIOD_LENGTH):
            self.state = TrafficLightState.YELLOW.value
        else:
            self.state = TrafficLightState.GREEN.value

    def get_state(self) -> Dict[str, Any]:
        return {
            "id": self.identifier,
            "position_on_route": self.position_on_route,
            "lon": self.lon,
            "lat": self.lat,
            "period": self.period,
            "ratio": self.ratio,
            "state": self.state,
            "offset": self.offset,
            "t": self.t,
        }

    def get_vehicle_input(self) -> Dict[str, Any]:
        return {
            "id": self.identifier,
            "position_on_route": self.position_on_route,
            "state": self.state,
            "period": self.period,
            "ratio": self.ratio,
            "t": self.t,
        }

    def get_position_on_route(self) -> Optional[float]:
        return self.position_on_route

    def html_overview(self) -> Optional[str]:
        return _load_resource("overview.html")

    def html_indicator(self) -> Optional[str]:
        return _load_resource("indicator.html")

    def html_tooltip(self) -> Optional[str]:
        return _load_resource("tooltip.html")

    def css_styles(self) -> Optional[str]:
        return _load_resource("style.css")

    def script_module(self) -> Optional[str]:
        return _load_resource("script.js")


class TrafficLightModelFactory(SimulationModelFactory):

    def __init__(self) -> None:
        self.next_identifier = 0

    def create(self, config: Any, route: Route) -> Optional[TrafficLightModel]:
        position_on_route = float(config.attrib["position_on_track"])
        period = float(config.attrib["period"])
        ratio = float(config.attrib["ratio"])

        track_point = route.get_track_point_by_dist(position_on_route)
        model = TrafficLightModel(
            identifier=self.next_identifier,
            position_on_route=position_on_route,
            lon=track_point.longitude,
            lat=track_point.latitude,
            period=period,
            ratio=ratio,
        )
        self.next_identifier += 1
        return model


def _load_resource(filename: str) -> str:
    resource_path = RESOURCES_DIR / filename
    return resource_path.read_text(encoding="utf-8")
