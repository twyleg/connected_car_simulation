import time
from route import Route
from typing import List, Dict
from random import randint
from enum import Enum


class TrafficLightState(Enum):
    RED = 'red'
    YELLOW = 'yellow'
    GREEN = 'green'


class TrafficLight:

    NUM_TRAFFIC_LIGHTS = 0
    YELLOW_PERIOD_LENGTH = 1

    def __init__(self, position_on_track: float, lon: float, lat: float, period: float, ratio: float):
        self.id = self.create_id()
        self.position_on_track = position_on_track
        self.lon = lon
        self.lat = lat
        self.period = period
        self.ratio = ratio
        self.state = TrafficLightState.RED
        self.offset = randint(0, period)
        self.t = 0

    def create_id(self) -> int:
        new_id = TrafficLight.NUM_TRAFFIC_LIGHTS
        TrafficLight.NUM_TRAFFIC_LIGHTS = TrafficLight.NUM_TRAFFIC_LIGHTS + 1
        return new_id

    def update(self, simulation_time: float) -> None:
        self.t = (simulation_time + self.offset) % self.period
        red_period_length = self.period * self.ratio
        if self.t < red_period_length:
            self.state = TrafficLightState.RED.value
        elif self.t < (red_period_length + self.YELLOW_PERIOD_LENGTH):
            self.state = TrafficLightState.YELLOW.value
        else:
            self.state = TrafficLightState.GREEN.value

    def get_output(self) -> Dict:
        return {
            'id': self.id,
            'position_on_route': self.position_on_track,
            'state': self.state,
            'period': self.period,
            'ratio': self.ratio,
            't': self.t
        }


class TrafficLightsManager:

    def __init__(self, traffic_lights_config: Dict, route: Route):
        self.route = route
        self.traffic_lights = self.create_traffic_lights(traffic_lights_config)

    def create_traffic_lights(self, traffic_lights_config: Dict) -> List[TrafficLight]:
        traffic_lights: List[TrafficLight] = []

        for traffic_light_definition in traffic_lights_config:
            position_on_track = float(traffic_light_definition.attrib['position_on_track'])
            period = float(traffic_light_definition.attrib['period'])
            ratio = float(traffic_light_definition.attrib['ratio'])

            track_point = self.route.get_track_point_by_dist(position_on_track)
            traffic_light = TrafficLight(position_on_track, track_point.longitude, track_point.latitude, period, ratio)
            traffic_lights.append(traffic_light)
        return traffic_lights

    def update(self) -> None:
        current_timestamp = time.time()

        for traffic_light in self.traffic_lights:
            traffic_light.update(current_timestamp)

    def get_traffic_lights_state(self) -> List[Dict]:
        return [traffic_light.__dict__ for traffic_light in self.traffic_lights]
