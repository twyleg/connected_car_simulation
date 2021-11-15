import os
from setuptools import find_packages, setup
from setuptools.command.install import install
import PyInstaller.__main__
import shutil

VERSION = '0.0.1'

class PyinstallerCommand(install):

    OUTPUT_DIR = f'dist/connected_car_simulation_{VERSION}'
    ARCHIVE_NAME = f'connected_car_simulation_{VERSION}'

    def run(self):
        shutil.rmtree(self.OUTPUT_DIR, ignore_errors=True)
        PyInstaller.__main__.run([
            'connected_car_simulation/simulator.py',
            '--paths', 'connected_car_simulation',
            '--distpath', self.OUTPUT_DIR,
            '--specpath', 'build/',
            '--onefile',
            '--windowed',
            '--console'
        ])
        shutil.copytree('static/', self.OUTPUT_DIR + '/static')
        shutil.copytree('examples/', self.OUTPUT_DIR + '/examples')
        shutil.copy('config.xml', self.OUTPUT_DIR + '/config.xml')
        shutil.make_archive(
            'dist/' + self.ARCHIVE_NAME,
            'zip',
            root_dir='dist/',
            base_dir=f'connected_car_simulation_{VERSION}',
        )


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="connected_car_simulation",
    version=VERSION,
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
    ],
    cmdclass={
        'pyinstaller': PyinstallerCommand
    }
)
