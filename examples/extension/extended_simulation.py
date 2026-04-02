import asyncio
from pathlib import Path

from connected_car_simulation.simulation import ConnectedCarSimulation
from examples.extension.models.example_model import ExampleModelFactory


FILE_DIR = Path(__file__).parent


async def run() -> None:
    connected_car_simulation = ConnectedCarSimulation(
        config_file_path=FILE_DIR / "config.xml",
    )
    connected_car_simulation.load_builtin_models()
    connected_car_simulation.load_custom_model(model_factory=ExampleModelFactory, config_tag="ExampleModel")
    await connected_car_simulation.run()


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
