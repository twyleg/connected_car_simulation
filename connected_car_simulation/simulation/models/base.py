from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional

from connected_car_simulation.simulation.route import Route


@dataclass(frozen=True)
class SimulationStepContext:
    route: Route
    vehicle_state: Dict[str, Any]
    previous_simulation_state: Dict[str, Any]
    simulation_timestamp: float


class SimulationModel(ABC):

    @property
    @abstractmethod
    def model_id(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def model_type(self) -> str:
        raise NotImplementedError

    @property
    def display_name(self) -> str:
        return self.model_id

    @abstractmethod
    def update(self, context: SimulationStepContext) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_vehicle_input(self) -> Any:
        raise NotImplementedError

    def get_position_on_route(self) -> Optional[float]:
        return None

    def html_overview(self) -> Optional[str]:
        return None

    def html_indicator(self) -> Optional[str]:
        return None

    def html_tooltip(self) -> Optional[str]:
        return None

    def css_styles(self) -> Optional[str]:
        return None

    def script_module(self) -> Optional[str]:
        return None

    def get_simulation_state(self, route: Route) -> Dict[str, Any]:
        state = self.get_state()
        map_position = self._get_map_position(route, state)
        return {
            "model_id": self.model_id,
            "model_type": self.model_type,
            "display_name": self.display_name,
            "state": state,
            "map_position": map_position,
            "ui": {
                "overview_html": self.html_overview(),
                "indicator_html": self.html_indicator(),
                "tooltip_html": self.html_tooltip(),
                "style_css": self.css_styles(),
                "script_js": self.script_module(),
            },
        }

    def _get_map_position(self, route: Route, state: Dict[str, Any]) -> Optional[Dict[str, float]]:
        if "lon" in state and "lat" in state:
            return {
                "lon": float(state["lon"]),
                "lat": float(state["lat"]),
            }

        position_on_route = state.get("position_on_route", self.get_position_on_route())
        if position_on_route is None:
            return None

        track_point = route.get_track_point_by_dist(float(position_on_route))
        return {
            "lon": track_point.longitude,
            "lat": track_point.latitude,
        }


class SimulationModelFactory(ABC):

    @abstractmethod
    def create(self, config: Any, route: Route) -> Optional[SimulationModel]:
        raise NotImplementedError
