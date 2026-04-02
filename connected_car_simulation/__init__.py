# Copyright (C) 2026 twyleg
from . import _version
from connected_car_simulation.simulation import ConnectedCarSimulation

__version__ = _version.get_versions()["version"]

__all__ = [
    "ConnectedCarSimulation",
    "__version__",
]
