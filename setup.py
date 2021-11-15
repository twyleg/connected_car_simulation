import os
from setuptools import find_packages, setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="connected_car_simulation",
    version="0.0.1",
    author="Torsten Wylegala",
    author_email="mail@twyleg.de",
    description=("Simulation to experiment with connected car features"),
    license="GPL 3.0",
    keywords="connected car simulation",
    url="https://github.com/twyleg/connected_car_simulation",
    packages=find_packages(),
    long_description=read('README.md'),
    install_requires=[
        'websockets',
        'aiohttp',
        'gpxpy'
    ]
)
