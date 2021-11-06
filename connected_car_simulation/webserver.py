import asyncio
import pathlib
import os
from aiohttp import web, web_response


ROOT_DIR = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))


class WebServer:

    def __init__(self, hostname: str, port: int):
        self.app = web.Application()
        self.app.router.add_get('/api/status', self.status_handler)
        self.app.router.add_static('/static/',
                              path=ROOT_DIR / 'static',
                              name='static')

        runner = web.AppRunner(self.app)
        asyncio.get_event_loop().run_until_complete(runner.setup())
        site = web.TCPSite(runner, hostname, port)
        self.webserver_coroutine = site.start()

    def start(self) -> None:
        asyncio.get_event_loop().run_until_complete(self.webserver_coroutine)

    async def status_handler(self, request) -> web_response.Response:
        return web.json_response('OK')
