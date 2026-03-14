import asyncio
import signal
import xml.etree.ElementTree as ET
from contextlib import suppress
from pathlib import Path

from typing import Dict

from connected_car_simulation.simulation_environment import SimulationEnvironment
from connected_car_simulation.resource_path import get_resource_path
from connected_car_simulation.websocket import Websocket
from connected_car_simulation.webserver import WebServer


FILE_DIR = Path(__file__).parent


async def simulation_updater_and_publisher(simulation_environment: SimulationEnvironment, websocket: Websocket):
    while True:
        simulation_environment.update()
        simulation_state = simulation_environment.get_simulation_state()
        await websocket.publish_simulation_state(simulation_state)
        await asyncio.sleep(0.1)


def read_config(config_file_path: Path) -> Dict:
    tree = ET.parse(config_file_path)
    return tree.getroot()


async def run() -> None:
    config = read_config(FILE_DIR / 'resources/config.xml')

    simulation_environment = SimulationEnvironment(route_file_path=FILE_DIR / 'resources/ui/routes/ostfalia-wf-wob.gpx',
                                                   config=config)
    simulation_environment.vehicle.acceleration = 0.0
    simulation_environment.vehicle.set_target_velocity_in_kmh(0.0)

    websocket = Websocket('0.0.0.0', 8081)
    await websocket.start()

    webserver = WebServer(simulation_environment, '0.0.0.0', 8080)
    await webserver.start()

    print('Connected Car Simulation started!')
    print('Open http://localhost:8080/static/index.html in your browser.')
    print('API documentation: http://localhost:8080/api/docs')

    updater_task = asyncio.create_task(
        simulation_updater_and_publisher(simulation_environment, websocket)
    )
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop_event.set)
        except NotImplementedError:
            pass

    try:
        await stop_event.wait()
    finally:
        updater_task.cancel()
        with suppress(asyncio.CancelledError):
            await updater_task
        await websocket.stop()
        await webserver.stop()


def main() -> None:
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
