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
import numpy as np
import tqdm
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt

# Local imports
import medenv

logging.basicConfig(level=logging.INFO)
features = [
    "bathymetry",
    "sea-surface-temperature",
    "sea-surface-salinity",
    "temperature",
    "salinity",
    "chlorophyl-a",
    "nitrate",
    "phosphate",
    "ammonium",
]
# features = medenv.Fetcher._available_features

fetcher = medenv.Fetcher(features)
logging.info(f"The available features are : {medenv.Fetcher._available_features}")

date = datetime.datetime(year=2016, month=1, day=1)
long0, lat0 = 5, 40
depth = 1000
values, info_values = fetcher.get_values(date, (long0, lat0), depth)
print(values)


feature = "salinity"
fetcher = medenv.Fetcher([feature])
date = datetime.datetime(year=2016, month=1, day=1)
depth = 1
longitude_range = [0, 10]
latitude_range = [36, 45]
resolution = 0.25
long_values = np.arange(longitude_range[0], longitude_range[1], step=resolution)
lat_values = np.arange(latitude_range[0], latitude_range[1], step=resolution)
Xlong, Ylat = np.meshgrid(long_values, lat_values)
Z = np.zeros_like(Xlong, dtype=float)
for ilong in tqdm.tqdm(range(Xlong.shape[0])):
    for jlat in range(Xlong.shape[1]):
        long_lat = (Xlong[ilong, jlat], Ylat[ilong, jlat])
        values, info_values = fetcher.get_values(date, long_lat, depth)
        Z[ilong, jlat] = values[feature]


fig = plt.figure(figsize=(8, 8))
ax = plt.subplot(111, projection=ccrs.PlateCarree())
ax.set_extent([*longitude_range, *latitude_range], crs=ccrs.PlateCarree())
ax.add_feature(cfeature.COASTLINE)

cm = ax.pcolormesh(
    long_values,
    lat_values,
    Z,
    transform=ccrs.PlateCarree(),
)
plt.colorbar(cm)

plt.show()
