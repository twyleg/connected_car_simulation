import logging
from pathlib import Path

from aiohttp import web, web_request, web_response

from connected_car_simulation.infrastructure.openapi import create_openapi_spec
from connected_car_simulation.infrastructure.resource_loader import load_text_resource
from connected_car_simulation.simulation.simulation_api import (
    InvalidSimulationRequestError,
    SimulationApi,
    UnknownSimulationActionError,
)
from connected_car_simulation.simulation.simulation_environment import SimulationEnvironment


FILE_DIR = Path(__file__).resolve().parent.parent
logger = logging.getLogger(__name__)


class WebServer:

    def __init__(self, simulation_environment: SimulationEnvironment, hostname: str, port: int) -> None:
        self.simulation_environment = simulation_environment
        self.api = SimulationApi(simulation_environment)
        self.hostname = hostname
        self.port = port
        self.app = web.Application()
        self.app.router.add_get('/api/openapi.json', self.openapi_handler)
        self.app.router.add_get('/api/docs', self.swagger_ui_handler)
        self.app.router.add_get('/api/actions/{action}', self.api_handler)
        self.app.router.add_static('/static/',
                              path=FILE_DIR / 'resources/ui/',
                              name='static')
        self.runner = web.AppRunner(self.app)
        self.site = None

    async def start(self) -> None:
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.hostname, self.port)
        await self.site.start()
        logger.info("HTTP server listening on http://%s:%s", self.hostname, self.port)

    async def stop(self) -> None:
        await self.runner.cleanup()
        self.site = None
        logger.info("HTTP server stopped")

    async def api_handler(self, request: web_request.BaseRequest) -> web_response.Response:
        action = request.match_info["action"]
        request_data = dict(request.query)

        logger.debug("HTTP API request: action=%s params=%s", action, request_data)

        try:
            response_data = self.api.invoke_action(action, request_data)
        except UnknownSimulationActionError as exc:
            return web.json_response(status=404, data={"error": str(exc), "action": action})
        except InvalidSimulationRequestError as exc:
            return web.json_response(status=400, data={"error": str(exc), "action": action})

        return web.json_response(status=200, data=response_data)

    async def openapi_handler(self, request: web_request.BaseRequest) -> web_response.Response:
        server_url = f"{request.scheme}://{request.host}"
        return web.json_response(create_openapi_spec(server_url))

    async def swagger_ui_handler(self, request: web_request.BaseRequest) -> web_response.Response:
        html = load_text_resource("swagger_ui.html")
        return web.Response(text=html, content_type='text/html')
