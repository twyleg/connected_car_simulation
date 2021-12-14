import time
from route import Route
from typing import List, Dict
from random import randint
from enum import Enum


class SpeedLimitLightSignal:

    NUM_SPEED_LIMIT_LIGHT_SIGNALS = 0
    YELLOW_PERIOD_LENGTH = 1

    def __init__(self, position_on_track: float, lon: float, lat: float, limit: int):
        self.id = self.create_id()
        self.position_on_track = position_on_track
        self.lon = lon
        self.lat = lat
        self.limit = limit

    def create_id(self) -> int:
        new_id = SpeedLimitLightSignal.NUM_SPEED_LIMIT_LIGHT_SIGNALS
        SpeedLimitLightSignal.NUM_SPEED_LIMIT_LIGHT_SIGNALS = SpeedLimitLightSignal.NUM_SPEED_LIMIT_LIGHT_SIGNALS + 1
        return new_id

    def get_output(self) -> Dict:
        return {
            'id': self.id,
            'position_on_route': self.position_on_track,
            'limit': self.limit
        }


class SpeedLimitLightSignalsManager:

    def __init__(self, traffic_lights_config: Dict, route: Route):
        self.route = route
        self.speed_limit_light_signals = self.create_speed_limit_light_signals(traffic_lights_config)

    def create_speed_limit_light_signals(self, speed_limit_light_signals_config: Dict) -> List[SpeedLimitLightSignal]:
        speed_limit_light_signals: List[SpeedLimitLightSignal] = []

        for speed_limit_light_signal_definition in speed_limit_light_signals_config:
            position_on_track = float(speed_limit_light_signal_definition.attrib['position_on_track'])
            limit = float(speed_limit_light_signal_definition.attrib['limit'])

            track_point = self.route.get_track_point_by_dist(position_on_track)
            speed_limit_light_signal = SpeedLimitLightSignal(position_on_track, track_point.longitude, track_point.latitude, limit)
            speed_limit_light_signals.append(speed_limit_light_signal)
        return speed_limit_light_signals

    def get_speed_limit_light_signals_state(self) -> List[Dict]:
        return [speed_limit_light_signal.__dict__ for speed_limit_light_signal in self.speed_limit_light_signals]
