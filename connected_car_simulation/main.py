#!/usr/bin/env python
import asyncio
import logging

from connected_car_simulation.simulation.connected_car_simulation import ConnectedCarSimulation


logger = logging.getLogger(__name__)

async def run() -> None:
    connected_car_simulation = ConnectedCarSimulation()
    connected_car_simulation.load_builtin_models()
    await connected_car_simulation.run()


def main() -> None:
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        logger.info('Connected car simulation interrupted')

if __name__ == '__main__':
    main()
