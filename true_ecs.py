#!/usr/bin/env python3
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


class Config:
    def __init__(self, fn):
        self.data_directory = "."
        self.image_filename = "{target}.fits"
        self.data_filename = "{target}.txt"
        self.custom_data_column_names = None
        self.wcs_filename = "{target}_wcs.fits"
        self.overwrite_wcs_file = False
        self.custom_scale_bounds = None
        self.transform_to_icrs = False
        self.output_filename = "{target}_ecs.csv"
        self.overwrite_output_file = True
        self.targets = None

        # Load configuration file
        with open(fn, "r") as f:
            conf_yaml = yaml.load(f, Loader=yaml.FullLoader)

        self.__dict__.update(conf_yaml)

        if not self.astrometry_api_key:
            raise Exception("The 'astrometry_api_key' option must be set up.")

        if not self.targets:
            raise Exception("No targets defined.")

        self.data_directory = os.path.expanduser(self.data_directory)


if __name__ == '__main__':
    try:
        cfg = Config("config.yaml")
    except Exception as e:
        print("Failed to load config file:", e)
        sys.exit(-1)

    client = Client()
    client.login(cfg.astrometry_api_key)

    for target in cfg.targets:
        print("-------------------------------------------")
        print(f"TARGET: {target}")
        data_dir_pattern = cfg.data_directory.format(target=target)
        for data_dir in glob.glob(data_dir_pattern):
            print("-------------------------------------------")
            print(f"Found in: {data_dir}")
            wcsfn = cfg.wcs_filename.format(target=target)
            wcs_file_path = os.path.join(data_dir, wcsfn)
            # Retrieve WCS solution if file does not exist or if user enforced
            # the query using the 'overwrite_wcs_file' option.
            if not os.path.exists(wcs_file_path) or cfg.overwrite_wcs_file:
                imagefn = cfg.image_filename.format(target=target)
                image_file_path = os.path.join(data_dir, imagefn)
                if not os.path.exists(image_file_path):
                    print(f"Error: {imagefn} not found: Cannot query WCS "
                          "solution for this directory.  Skipping.")
                    continue

                print(f"{imagefn} found: Querying WCS solution...")
                if cfg.custom_scale_bounds and \
                   len(cfg.custom_scale_bounds) == 2:
                    kwargs = dict(scale_lower=cfg.custom_scale_bounds[0],
                                  scale_upper=cfg.custom_scale_bounds[1],
                                  scale_type='ul',
                                  scale_units='degwidth')
                client.retrieve_corrected_wcs(image_file_path, wcs_file_path,
                                              **kwargs)
            else:
                print(f"Info: {wcsfn} found: Skipping WCS solution for this "
                      "directory.")

            outputfn = cfg.output_filename.format(target=target)
            output_file_path = os.path.join(data_dir, outputfn)
            if os.path.exists(output_file_path) and \
               not cfg.overwrite_output_file:
                print(f"Info: {outputfn} found: Skipping ECS calculation for "
                      "this directory.")
                continue

            datafn = cfg.data_filename.format(target=target)
            data_file_path = os.path.join(data_dir, datafn)
            if not os.path.exists(data_file_path):
                print(f"Error: {datafn} not found: Cannot calculate ECS for "
                      "this directory.  Skipping.")
                continue

            print(f"{datafn} found: Converting X,Y coordinates to ECS...")
            data_t = Table.read(data_file_path,
                                format='ascii', delimiter='\\s',
                                names=cfg.custom_data_column_names)
            with fits.open(wcs_file_path) as f:
                w = WCS(f[0].header)
                sky = w.pixel_to_world(data_t['X'], data_t['Y'])
                if cfg.transform_to_icrs:
                    print("Transforming ECS to ICRS frame...")
                    sky = sky.transform_to(ICRS)
                ecs_t = sky.to_table()
                ecs_t.rename_column('ra', 'RA')
                ecs_t.rename_column('dec', 'DEC')

            print(f"Writing {outputfn}...")
            hstack([ecs_t, data_t]).write(output_file_path, format='csv',
                                          overwrite=True)
