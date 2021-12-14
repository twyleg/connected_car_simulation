from route import Route
from vehicle import Vehicle
from traffic_lights import TrafficLightsManager, TrafficLight
from speed_limit_light_signals import SpeedLimitLightSignalsManager, SpeedLimitLightSignal
from typing import Dict, List


class SimulationEnvironment:

    def __init__(self,
                 route_file_path: str,
                 config: Dict):
        self.route = Route(route_file_path, config.find('SpeedLimits'))
        self.vehicle = Vehicle(config.find('Vehicle'), self.route)
        self.traffic_lights_manager = TrafficLightsManager(config.find('TrafficLights'), self.route)
        self.speed_limit_light_signals_manager = SpeedLimitLightSignalsManager(config.find('SpeedLimitLightSignals'), self.route)

    def update(self) -> None:
        self.vehicle.update()
        self.traffic_lights_manager.update()

    def set_vehicle_position(self, position: float):
        self.vehicle.set_position_on_route(position)

    def get_simulation_state(self) -> Dict:
        simulation_state = {
            'vehicle_state': self.vehicle.get_vehicle_state(),
            'traffic_lights_state': self.traffic_lights_manager.get_traffic_lights_state(),
            'speed_limit_light_signals_state': self.speed_limit_light_signals_manager.get_speed_limit_light_signals_state()
        }
        return simulation_state

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

    def get_traffic_lights_in_range(self, range: int) -> List[TrafficLight]:
        traffic_lights_in_range: List[TrafficLight] = []
        min_pos = self.vehicle.position_on_route - 10
        max_pos = self.vehicle.position_on_route + range

        for traffic_light in self.traffic_lights_manager.traffic_lights:
            if min_pos < traffic_light.position_on_track < max_pos:
                traffic_lights_in_range.append(traffic_light)
        return traffic_lights_in_range

    def get_speed_limit_light_signals_in_range(self, range: int) -> List[SpeedLimitLightSignal]:
        speed_limit_light_signals_in_range: List[SpeedLimitLightSignal] = []
        min_pos = self.vehicle.position_on_route - 10
        max_pos = self.vehicle.position_on_route + range

        for speed_limit_light_signal in self.speed_limit_light_signals_manager.speed_limit_light_signals:
            if min_pos < speed_limit_light_signal.position_on_track < max_pos:
                speed_limit_light_signals_in_range.append(speed_limit_light_signal)
        return speed_limit_light_signals_in_range

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
            'traffic_lights': [traffic_light.get_output() for traffic_light in
                               self.get_traffic_lights_in_range(radio_range)],
            'speed_limit_light_signals': [speed_limit_light_signal.get_output() for speed_limit_light_signal in
                                          self.get_speed_limit_light_signals_in_range(radio_range)]
        }
        return vehicle_input

    def get_vehicle_input_infrastructure(self) -> Dict:
        vehicle_input = {
            'vehicle_state': self.get_vehicle_state(),
            'map': self.get_map_data(),
            'traffic_lights': [traffic_light.get_output() for traffic_light in
                               self.traffic_lights_manager.traffic_lights],
            'speed_limit_light_signals': [speed_limit_light_signal.get_output() for speed_limit_light_signal in
                                          self.speed_limit_light_signals_manager.speed_limit_light_signals]
        }
        return vehicle_input
