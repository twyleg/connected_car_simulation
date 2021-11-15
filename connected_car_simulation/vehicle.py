import time
from route import Route
from typing import Dict
from gpxpy.gpx import GPXTrackPoint


class Vehicle:

    def __init__(self, config: Dict, route: Route):
        self.route = route
        self.max_acceleration = float(config.find('MaxAcceleration').text)
        self.max_velocity = float(config.find('MaxVelocity').text)
        self.radio_range = float(config.find('RadioRange').text)
        self.acceleration = 0.0
        self.current_velocity = 0.0
        self.target_velocity = 0.0
        self.position_coordinates: GPXTrackPoint
        self.position_on_route = 0.0
        self.last_update_timestamp = time.time()

    def set_target_velocity_in_ms(self, target_velocity: float) -> None:
        self.target_velocity = target_velocity

    def set_target_velocity_in_kmh(self, target_velocity: float) -> None:
        self.target_velocity = min(target_velocity, self.max_velocity) / 3.6

    def set_acceleration(self, acceleration: float) -> None:
        self.acceleration = min(acceleration, self.max_acceleration)

    def set_position_on_route(self, position):
        self.position_on_route = min(position, len(self.route.waypoints))

    def get_velocity_in_kmh(self) -> float:
        return self.current_velocity * 3.6

    def get_velocity_in_ms(self) -> float:
        return self.current_velocity

    def get_vehicle_state(self) -> Dict:
        vehicle_state = {
            "max_acceleration": self.acceleration,
            "target_velocity": self.target_velocity,
            "current_velocity": self.current_velocity,
            "position_coordinates": {
                "lon": self.position_coordinates.longitude,
                "lat": self.position_coordinates.latitude
            },
            "position_on_route": self.position_on_route
        }
        return vehicle_state

    def update(self) -> None:
        current_timestamp = time.time()
        delta_time = current_timestamp - self.last_update_timestamp

        if abs(self.current_velocity - self.target_velocity) < 0.5:
            self.current_velocity = self.target_velocity
        else:
            acceleration = self.acceleration if self.current_velocity < self.target_velocity else -self.acceleration
            self.current_velocity = self.current_velocity + (acceleration * delta_time)

        driven_distance = (self.current_velocity + ((self.current_velocity - self.current_velocity) / 2)) * delta_time
        self.position_on_route = self.position_on_route + driven_distance
        self.position_coordinates = self.route.get_track_point_by_dist(self.position_on_route)
        self.last_update_timestamp = current_timestamp


