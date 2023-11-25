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
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np

# Local imports
import medenv

logging.basicConfig(level=logging.INFO)

# Get depth measures
long0, lat0 = 5, 40
depth, _ = medenv.etopo.get_value(long0, lat0)
d_depth, _ = medenv.etopo.get_dvalue(long0, lat0)
print(
    f"The depth from etopo1 at {long0}° east, {lat0}° north is {depth} m. with a steep of {d_depth} m./°"
)

# Show the mediterannean sea
fig = plt.figure(figsize=(8, 8))

longitude_range = [0, 10]
latitude_range = [36, 45]

ax = plt.subplot(111, projection=ccrs.PlateCarree())
ax.set_extent([*longitude_range, *latitude_range], crs=ccrs.PlateCarree())
ax.add_feature(cfeature.COASTLINE)

longidx_min = np.fabs(medenv.etopo.longvals - longitude_range[0]).argmin()
longidx_max = np.fabs(medenv.etopo.longvals - longitude_range[1]).argmin()
latidx_min = np.fabs(medenv.etopo.latvals - latitude_range[0]).argmin()
latidx_max = np.fabs(medenv.etopo.latvals - latitude_range[1]).argmin()
cm = ax.pcolormesh(
    medenv.etopo.longvals[longidx_min:longidx_max],
    medenv.etopo.latvals[latidx_min:latidx_max],
    medenv.etopo.depthvals[latidx_min:latidx_max, longidx_min:longidx_max],
    transform=ccrs.PlateCarree(),
)

plt.colorbar(cm)
plt.tight_layout()
plt.title("Depth (m.)")
plt.savefig("example-001-depth.png")

fig = plt.figure(figsize=(8, 8))
ax = plt.subplot(111, projection=ccrs.PlateCarree())
ax.set_extent([*longitude_range, *latitude_range], crs=ccrs.PlateCarree())
ax.add_feature(cfeature.COASTLINE)

longidx_min = np.fabs(medenv.etopo.longvals - longitude_range[0]).argmin()
longidx_max = np.fabs(medenv.etopo.longvals - longitude_range[1]).argmin()
latidx_min = np.fabs(medenv.etopo.latvals - latitude_range[0]).argmin()
latidx_max = np.fabs(medenv.etopo.latvals - latitude_range[1]).argmin()
cm = ax.pcolormesh(
    medenv.etopo.longvals[longidx_min:longidx_max],
    medenv.etopo.latvals[latidx_min:latidx_max],
    medenv.etopo.derivative_depthvals[latidx_min:latidx_max, longidx_min:longidx_max],
    transform=ccrs.PlateCarree(),
)

plt.colorbar(cm)

plt.tight_layout()
plt.title("Gradient (m/°)")
plt.savefig("example-001-gradient.png")

plt.show()
