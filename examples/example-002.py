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

# External imports
import tqdm
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np

# Local imports
import medenv

long0, lat0, depth = 5, 40, 120

print(f"For location {long0}° east, {lat0}° north, at {depth} m")
# for what in medenv.woa._AVAILABLE_MEASURES:
#     value = medenv.woa.get_value((long0, lat0), depth, what)
#     print(f"   {what} : {value}")
value = medenv.woa.is_land((long0, lat0))

# First way to sample the measures by
# requesting by long/lat/depth
# This is inefficient but done here

longitude_range = [0, 10]
latitude_range = [36, 45]
resolution = 0.25  # medenv.woa._DEFAULT_RESOLUTION
long_values = np.arange(longitude_range[0], longitude_range[1], step=resolution)
lat_values = np.arange(latitude_range[0], latitude_range[1], step=resolution)
Xlong, Ylat = np.meshgrid(long_values, lat_values)
Z = np.zeros_like(Xlong, dtype=float)
for ilong in tqdm.tqdm(range(Xlong.shape[0])):
    for jlat in range(Xlong.shape[1]):
        long_lat = (Xlong[ilong, jlat], Ylat[ilong, jlat])
        if medenv.woa.is_land(long_lat):
            value = np.nan
        else:
            value = medenv.woa.get_value(
                long_lat,
                depth,
                "temperature",
                resolution=resolution,
            )

        Z[ilong, jlat] = value

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
