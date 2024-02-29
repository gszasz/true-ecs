#!/usr/bin/env python
"""Calculate true ECS coordinates using corrected WCS parameters.

Copyright (C) 2024  Gabriel Szász
SPDX-License-Identifier: GPL-3.0-or-later

This file is part of True-ECS.

True-ECS is free software: you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

True-ECS is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
True-ECS.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import sys
import yaml
import glob
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import ICRS
from astropy.table import Table, hstack

from astrometry_api import Client


if __name__ == '__main__':
    # Load configuration file
    with open("config.yaml", "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    api_key = config['astrometry_api_key']

    if not api_key:
        print("The 'astrometry_api_key' option must be set up.")
        print("Fatal error.  Terminating.")
        sys.exit(-1)

    c = Client()
    c.login(api_key)

    for target in config['targets']:
        print()
        print(f"TARGET: {target}")
        print("-------------------------------------------")
        path = config['data_directory'].format(target=target)
        path = os.path.expanduser(path)
        for directory in glob.glob(path):
            print(f"Found in: {directory}")
            wcsfn = config['wcs_filename'].format(target=target)
            wcsfn = f"{directory}/{wcsfn}"
            # Retrieve wcs file if it does not exist
            if not os.path.exists(wcsfn):
                imagefn = config['image_filename'].format(target=target)
                imagefn = f"{directory}/{imagefn}"
                if os.path.exists(imagefn):
                    print("{fn} found...".format(fn=os.path.basename(imagefn)),
                          "querying WCS solution")
                    c.retrieve_corrected_wcs(imagefn, wcsfn)
                else:
                    print(f"File {imagefn} does not exist.")
                    print("Fatal error.  Terminating.")
                    sys.exit(-1)
            else:
                print("WCS solution was already done for this target. ",
                      "Skipping...")

            datafn = config['data_filename'].format(target=target)
            datafn = f"{directory}/{datafn}"
            if not os.path.exists(datafn):
                print(f"File {datafn} does not exist.")
                print("Fatal error.  Terminating.")
                sys.exit(-1)

            print("{fn} found.".format(fn=os.path.basename(datafn)),
                  "Converting X,Y coordinates to ECS...")
            data_t = Table.read(datafn, format='ascii', delimiter='\\s',
                                data_start=config['data_header_lines'],
                                names=config['data_columns'])
            with fits.open(wcsfn) as f:
                w = WCS(f[0].header)
                sky = w.pixel_to_world(data_t['X'], data_t['Y'])
                if config['transform_to_icrs']:
                    print("Transforming to ICRS frame...")
                    sky = sky.transform_to(ICRS)
                ecs_t = sky.to_table()
                ecs_t.rename_column('ra', 'RA')
                ecs_t.rename_column('dec', 'DEC')

            outputfn = config['output_filename'].format(target=target)
            outputfn = f"{directory}/{outputfn}"
            print("Writing {fn}...".format(fn=os.path.basename(outputfn)))
            hstack([ecs_t, data_t]).write(outputfn, format='csv',
                                          overwrite=True)
