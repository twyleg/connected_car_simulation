# Copyright (C) 2024 twyleg
import versioneer
from pathlib import Path
from setuptools import find_packages, setup


def read(relative_filepath):
    return open(Path(__file__).parent / relative_filepath).read()


def read_long_description() -> str:
    return read("README.md")


# fmt: off
setup(
    name="connected_car_simulation",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Torsten Wylegala",
    author_email="mail@twyleg.de",
    description="",
    license="GPL 3.0",
    keywords="",
    url="https://github.com/twyleg/connected_car_simulation",
    packages=find_packages(),
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=[
        "websockets",
        "aiohttp",
        "gpxpy"
    ],
    entry_points={
        "console_scripts": [
            "connected_car_simulation = connected_car_simulation.main:main",
        ]
    },
)