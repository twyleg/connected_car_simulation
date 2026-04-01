#!/usr/bin/env python
import json
import time
from typing import Any, Dict
from urllib.parse import urlencode
from urllib.request import urlopen

from simple_example_common import calculate_vehicle_output


HOSTNAME = "localhost:8080"
POLL_INTERVAL_SECONDS = 0.1


def get_vehicle_input_adhoc(hostname: str = HOSTNAME) -> Dict[str, Any]:
    with urlopen(f"http://{hostname}/api/actions/get_vehicle_input_adhoc") as response:
        return json.load(response)


def set_vehicle_output(target_velocity: float, acceleration: float, hostname: str = HOSTNAME) -> None:
    query = urlencode(
        {
            "target_velocity": target_velocity,
            "acceleration": acceleration,
        }
    )
    with urlopen(f"http://{hostname}/api/actions/set_vehicle_output?{query}"):
        pass


def main() -> None:
    while True:
        vehicle_input = get_vehicle_input_adhoc(hostname=HOSTNAME)
        vehicle_output = calculate_vehicle_output(vehicle_input)
        set_vehicle_output(
            target_velocity=vehicle_output["target_velocity"],
            acceleration=vehicle_output["acceleration"],
            hostname=HOSTNAME,
        )
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
