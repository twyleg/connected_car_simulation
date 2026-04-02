#!/usr/bin/env python
from typing import Any, Dict, List


DEFAULT_TARGET_VELOCITY = 50.0
DEFAULT_ACCELERATION = 2.0
STOP_ACCELERATION = 8.0
STOP_DISTANCE_THRESHOLD = 30.0


def get_next_traffic_light(vehicle_input: Dict[str, Any]) -> Dict[str, Any] | None:
    models: Dict[str, Any] = vehicle_input.get("models", {})
    traffic_lights: List[Dict[str, Any]] = models.get("traffic_lights", [])
    if not traffic_lights:
        return None
    return traffic_lights[0]


def calculate_vehicle_output(vehicle_input: Dict[str, Any]) -> Dict[str, float]:
    next_traffic_light = get_next_traffic_light(vehicle_input)
    if next_traffic_light is None:
        return {
            "target_velocity": DEFAULT_TARGET_VELOCITY,
            "acceleration": DEFAULT_ACCELERATION,
        }

    vehicle_position_on_route = vehicle_input["vehicle_state"]["position_on_route"]
    next_traffic_light_position = next_traffic_light["position_on_route"]
    distance_to_next_traffic_light = next_traffic_light_position - vehicle_position_on_route

    print(f"Distance to next traffic light: {distance_to_next_traffic_light:f}")

    if next_traffic_light["state"] == "red" and distance_to_next_traffic_light < STOP_DISTANCE_THRESHOLD:
        return {
            "target_velocity": 0.0,
            "acceleration": STOP_ACCELERATION,
        }

    return {
        "target_velocity": DEFAULT_TARGET_VELOCITY,
        "acceleration": DEFAULT_ACCELERATION,
    }
