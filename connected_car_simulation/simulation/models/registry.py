from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

from connected_car_simulation.simulation.models.base import (
    SimulationModel,
    SimulationModelFactory,
    SimulationStepContext,
)
from connected_car_simulation.simulation.models.traffic_lights import TrafficLightModelFactory
from connected_car_simulation.simulation.route import Route


@dataclass(frozen=True)
class ModelRegistration:
    factory: SimulationModelFactory
    config_tag: str


class SimulationModelRegistry:

    def __init__(self, route: Route, models: Iterable[SimulationModel]):
        self.route = route
        self.models = list(models)

    @classmethod
    def from_config(
        cls,
        config: Any,
        route: Route,
        registrations: Iterable[ModelRegistration],
    ) -> "SimulationModelRegistry":
        models: List[SimulationModel] = []
        for registration in registrations:
            for model_config in config.findall(f".//{registration.config_tag}"):
                model = registration.factory.create(model_config, route)
                if model is not None:
                    models.append(model)
        return cls(route, models)

    @staticmethod
    def builtin_registrations() -> List[ModelRegistration]:
        return [
            ModelRegistration(factory=TrafficLightModelFactory(), config_tag="TrafficLight"),
        ]

    def update(self, vehicle_state: Dict[str, Any], previous_simulation_state: Dict[str, Any]) -> None:
        simulation_timestamp = time.time()
        context = SimulationStepContext(
            route=self.route,
            vehicle_state=vehicle_state,
            previous_simulation_state=previous_simulation_state,
            simulation_timestamp=simulation_timestamp,
        )
        for model in self.models:
            model.update(context)

    def get_simulation_state(self) -> List[Dict[str, Any]]:
        return [model.get_simulation_state(self.route) for model in self.models]

    def get_model_ui_resources(self) -> Dict[str, Dict[str, Optional[str]]]:
        resources_by_model_type: Dict[str, Dict[str, Optional[str]]] = {}
        for model in self.models:
            resources_by_model_type.setdefault(model.model_type, model.get_ui_resources())
        return resources_by_model_type

    def get_vehicle_input(self, vehicle_state: Dict[str, Any], max_distance: Optional[float] = None) -> Dict[str, Any]:
        grouped_models: Dict[str, List[Any]] = {}
        vehicle_position = float(vehicle_state["position_on_route"])

        for model in self.models:
            position_on_route = model.get_position_on_route()
            if max_distance is not None and position_on_route is not None:
                min_position = vehicle_position - 10
                max_position = vehicle_position + max_distance
                if not (min_position < position_on_route < max_position):
                    continue

            grouped_models.setdefault(model.model_type, []).append(model.get_vehicle_input())

        return grouped_models
