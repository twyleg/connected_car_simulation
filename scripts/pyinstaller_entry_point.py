# Copyright (C) 2024 twyleg
from connected_car_simulation.main import main

#
# This separate entry point is necessary to make pyinstaller pick up the sdist package instead of the locally available
# "filesystem package". Without picking the sdist package, data files won't get included during the analyze step.
#

if __name__ == "__main__":
    main()