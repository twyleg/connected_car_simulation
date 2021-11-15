import asyncio
import xml.etree.ElementTree as ET

from simulation_environment import SimulationEnvironment
from websocket import Websocket
from webserver import WebServer
from typing import Dict


async def simulation_updater_and_publisher(simulation_environment: SimulationEnvironment, websocket: Websocket):
    while True:
        simulation_environment.update()
        simulation_state = simulation_environment.get_simulation_state()
        await websocket.publish_simulation_state(simulation_state)
        await asyncio.sleep(0.1)


def read_config(config_file_path: str) -> Dict:
    tree = ET.parse(config_file_path)
    return tree.getroot()


if __name__ == '__main__':

    config = read_config('config.xml')

    simulation_environment = SimulationEnvironment(route_file_path='static/routes/ostfalia-wf-wob.gpx',
                                                   config=config)
    simulation_environment.vehicle.acceleration = 0.0
    simulation_environment.vehicle.set_target_velocity_in_kmh(0.0)

    websocket = Websocket('0.0.0.0', 8081)
    websocket.start()

    webserver = WebServer(simulation_environment, '0.0.0.0', 8080)
    webserver.start()

    loop = asyncio.get_event_loop()
    taskOne = loop.create_task(simulation_updater_and_publisher(simulation_environment, websocket))
    loop.run_until_complete(asyncio.wait([taskOne]))

    loop.run_forever()
