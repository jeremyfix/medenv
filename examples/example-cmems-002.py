# coding: utf-8

"""
This script belongs to the medenv package
Copyright (C) 2022 Jeremy Fix

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

# Standard imports
import logging
import datetime

# External imports
import tqdm

# Local imports
import medenv

logging.basicConfig(level=logging.INFO)

features = [
    "sea-surface-temperature",
    "sea-surface-salinity",
    "bathymetry",
    "temperature",
    "salinity",
    "chlorophyl-a",
    "nitrate",
    "phosphate",
    "ammonium",
    "phytoplankton-carbon-biomass",
    "oxygen",
    "net-primary-production",
    "ph",
    "alkalinity",
    "dissolved-inorganic-carbon",
    "northward-water-velocity",
    "eastward-water-velocity",
    # 2D features
    "mixed-layer-thickness",
    "sea-surface-above-geoid",
    "surface-partial-pressure-co2",
    "surface-co2-flux",
]
# features = medenv.Fetcher._available_features

fetcher = medenv.Fetcher(features, reduction="mean")
logging.info(f"The available features are : {medenv.Fetcher._available_features}")

date = datetime.datetime(year=2012, month=9, day=22, hour=14)
# 1 degree is somehow 100 kms
long, lat = 13.63, 43.55
tol_spatial = 0.2
long0, lat0 = (long - tol_spatial / 2, long + tol_spatial / 2), (
    lat - tol_spatial / 2,
    lat + tol_spatial / 2,
)
# long0, lat0 = -2.95, 30.32
depth = 6
values, info_values = fetcher.get_values(date, (long0, lat0), depth)
print(values)
print(info_values)
