from typing import Any, Dict, Iterable

from connected_car_simulation.simulation.models import ModelRegistration, SimulationModelRegistry
from connected_car_simulation.simulation.route import Route
from connected_car_simulation.simulation.vehicle import Vehicle


class SimulationEnvironment:

    def __init__(self,
                 route_file_path: str,
                 config: Any,
                 model_registrations: Iterable[ModelRegistration]):
        self.route = Route(route_file_path, config.find('SpeedLimits'))
        self.vehicle = Vehicle(config.find('Vehicle'), self.route)
        self.models = SimulationModelRegistry.from_config(config, self.route, model_registrations)
        self.previous_simulation_state = self.get_simulation_state()

    def update(self) -> None:
        self.vehicle.update()
        self.models.update(self.vehicle.get_vehicle_state(), self.previous_simulation_state)
        self.previous_simulation_state = self.get_simulation_state()

    def set_vehicle_position(self, position: float):
        self.vehicle.set_position_on_route(position)

    def get_simulation_state(self) -> Dict:
        simulation_state = {
            'vehicle_state': self.vehicle.get_vehicle_state(),
            'models': self.models.get_simulation_state(),
        }
        return simulation_state

    def get_model_ui_resources(self) -> Dict[str, Dict[str, Any]]:
        return self.models.get_model_ui_resources()

    def get_route_information(self) -> Dict:
        simulation_state = {
            'length': self.route.get_length(),
            'start': {
                'lat': self.route.get_start_waypoint().latitude,
                'lon': self.route.get_start_waypoint().longitude
            },
            'end': {
                'lat': self.route.get_end_waypoint().latitude,
                'lon': self.route.get_end_waypoint().longitude
            }
        }
        return simulation_state

    def get_vehicle_state(self) -> Dict:
        return {
            'current_velocity': self.vehicle.get_velocity_in_kmh(),
            'max_acceleration': self.vehicle.acceleration,
            'position_on_route': self.vehicle.position_on_route
        }

    def get_map_data(self) -> Dict:
        return {
            'speed_limit': self.route.get_speed_limit_by_dist(self.vehicle.position_on_route)
        }

    def get_vehicle_input_adhoc(self) -> Dict:
        radio_range = self.vehicle.radio_range
        vehicle_input = {
            'vehicle_state': self.get_vehicle_state(),
            'map': self.get_map_data(),
            'models': self.models.get_vehicle_input(self.vehicle.get_vehicle_state(), max_distance=radio_range),
        }
        return vehicle_input

    def get_vehicle_input_infrastructure(self) -> Dict:
        vehicle_input = {
            'vehicle_state': self.get_vehicle_state(),
            'map': self.get_map_data(),
            'models': self.models.get_vehicle_input(self.vehicle.get_vehicle_state()),
        }
        return vehicle_input
