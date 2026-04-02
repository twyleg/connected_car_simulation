from __future__ import annotations

import asyncio
from copy import deepcopy
import logging
import signal
import xml.etree.ElementTree as ET
from contextlib import suppress
from pathlib import Path
from typing import Optional, Type

from connected_car_simulation.infrastructure.webserver import WebServer
from connected_car_simulation.infrastructure.websocket import Websocket
from connected_car_simulation.logging_utils import configure_logging
from connected_car_simulation.simulation.models import ModelRegistration, SimulationModelFactory, SimulationModelRegistry
from connected_car_simulation.simulation.simulation_environment import SimulationEnvironment


logger = logging.getLogger(__name__)


class ConnectedCarSimulation:

    def __init__(
        self,
        config_file_path: Optional[Path] = None,
        route_file_path: Optional[Path] = None,
        log_level: str = "INFO",
        http_host: str = "0.0.0.0",
        http_port: int = 8080,
        websocket_host: str = "0.0.0.0",
        websocket_port: int = 8081,
    ) -> None:
        configure_logging(log_level)
        package_dir = Path(__file__).resolve().parent.parent
        self.package_config_file_path = package_dir / "resources/config.xml"
        self.config_file_path = Path(config_file_path) if config_file_path is not None else None
        self.route_file_path = Path(route_file_path or (package_dir / "resources/ui/routes/ostfalia-wf-wob.gpx"))
        self.http_host = http_host
        self.http_port = http_port
        self.websocket_host = websocket_host
        self.websocket_port = websocket_port
        self.model_registrations: list[ModelRegistration] = []

    def load_builtin_models(self) -> None:
        self.model_registrations.extend(SimulationModelRegistry.builtin_registrations())

    def load_custom_model(self, model_factory: Type[SimulationModelFactory] | SimulationModelFactory, config_tag: str) -> None:
        factory = model_factory() if isinstance(model_factory, type) else model_factory
        self.model_registrations.append(ModelRegistration(factory=factory, config_tag=config_tag))

    def create_simulation_environment(self) -> SimulationEnvironment:
        config = self._load_config()
        return SimulationEnvironment(
            route_file_path=self.route_file_path,
            config=config,
            model_registrations=self.model_registrations,
        )

    def _load_config(self) -> ET.Element:
        package_config = ET.parse(self.package_config_file_path).getroot()

        if self.config_file_path is None:
            return package_config

        custom_config = ET.parse(self.config_file_path).getroot()
        return self._merge_config(package_config, custom_config)

    def _merge_config(self, base_config: ET.Element, override_config: ET.Element) -> ET.Element:
        merged_config = deepcopy(base_config)

        for override_child in override_config:
            existing_child = merged_config.find(override_child.tag)
            if existing_child is not None:
                merged_config.remove(existing_child)
            merged_config.append(deepcopy(override_child))

        return merged_config

    async def run(self) -> None:
        simulation_environment = self.create_simulation_environment()
        simulation_environment.vehicle.acceleration = 0.0
        simulation_environment.vehicle.set_target_velocity_in_kmh(0.0)

        websocket = Websocket(simulation_environment, self.websocket_host, self.websocket_port)
        await websocket.start()

        webserver = WebServer(simulation_environment, self.http_host, self.http_port)
        await webserver.start()

        logger.info("Connected Car Simulation started")
        logger.info("UI available at http://localhost:%s/static/index.html", self.http_port)
        logger.info("API documentation available at http://localhost:%s/api/docs", self.http_port)

        updater_task = asyncio.create_task(self._simulation_updater_and_publisher(simulation_environment, websocket))
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
            logger.info("Stopping connected car simulation")
            updater_task.cancel()
            with suppress(asyncio.CancelledError):
                await updater_task
            await websocket.stop()
            await webserver.stop()

    async def _simulation_updater_and_publisher(self, simulation_environment: SimulationEnvironment, websocket: Websocket):
        while True:
            simulation_environment.update()
            simulation_state = simulation_environment.get_simulation_state()
            await websocket.publish_simulation_state(simulation_state)
            await asyncio.sleep(0.1)
