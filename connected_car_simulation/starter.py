import asyncio
import time
from route import Route
from websocket import Websocket
from webserver import WebServer

i = 0
points = None
route = None
websocket = None


async def publisher():
    global i
    global route
    global websocket
    while True:
        print(f"loop {int(round(time.time() * 1000))}")
        waypoint = route.get_track_point_by_dist(i);
        i = i + 0.1
        await websocket.publish_position(waypoint)
        await asyncio.sleep(0.1)

if __name__ == '__main__':

    route = Route('static/ostfalia-wf-wob.gpx')

    websocket = Websocket("0.0.0.0", 8081)
    websocket.start()

    webserver = WebServer("0.0.0.0", 8080)
    webserver.start()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(publisher())
    loop.run_forever()
