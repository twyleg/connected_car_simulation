from connected_car_simulation.simulation.models.traffic_lights import (
    TrafficLightModel,
    TrafficLightModelFactory,
    TrafficLightState,
)


TrafficLight = TrafficLightModel
TrafficLightsManager = TrafficLightModelFactory

__all__ = [
    "TrafficLight",
    "TrafficLightModel",
    "TrafficLightModelFactory",
    "TrafficLightsManager",
    "TrafficLightState",
]
