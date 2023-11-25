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
import netCDF4
import numpy as np

# Local imports
from medenv import utils

# doi:10.7289/V5C8276M
BEDROCK_GRID_URL = "https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO1/data/bedrock/grid_registered/netcdf/ETOPO1_Bed_g_gmt4.grd.gz"

# The netCDF dataset id
#     Conventions: COARDS/CF-1.0
#    title: ETOPO1_Bed_g_gmt4.grd
#    GMT_version: 4.4.0
#    node_offset: 0
#    dimensions(sizes): x(21601), y(10801)
#    variables(dimensions): float64 x(x), float64 y(y), int32 z(y, x)
# with
# x : longitude,
#    long_name: Longitude
#    actual_range: [-180.  180.]
#    units: degrees_east
# y : latitude
#    long_name: Latitude
#    actual_range: [-90.  90.]
#    units: degrees_north
#
dataset = None
longvals = None
latvals = None
depthvals = None
derivate_dephvals = None


def fetch_values():
    global dataset, longvals, latvals, depthvals, derivative_depthvals
    if dataset is None:
        # Download the data archive and extract it
        logging.debug("Downloading the etopo1 data doi:10.7289/V5C8276M")
        filepath = utils.download_and_extract(BEDROCK_GRID_URL, "gzip", "eotop1.grd")
        # Load the CDF file
        dataset = netCDF4.Dataset(filepath)
        longvals = dataset.variables["x"][:]
        latvals = dataset.variables["y"][:]
        depthvals = dataset.variables["z"][:]
        # Compute the detta in longitude/latitude, assuming
        # constant sampling in each direction
        dlongitude = longvals[1] - longvals[0]
        dlatitude = latvals[1] - latvals[0]
        # The computation of the gradient takes some times
        # Maybe we could reduce this computational time by
        # restricting the values fetched
        # e.g. restricting to the mediterranean sea
        derivatives_depthvals = np.gradient(depthvals, dlongitude, dlatitude)
        derivative_depthvals = np.sqrt(
            derivatives_depthvals[0] ** 2 + derivatives_depthvals[1] ** 2
        )
        logging.debug(f"ETOPO1 netCDF dataset informations : \n {dataset}")


def get_value(longitude, latitude):
    """
    Return the depth from the closest longitude, latitude in etopo1

    Args:
        longitude : degrees east
        latitude : degrees north
    """
    fetch_values()
    assert (longvals.min() <= longitude <= longvals.max()) and (
        latvals.min() <= latitude <= latvals.max()
    )
    longidx = np.fabs(longvals - longitude).argmin()
    latidx = np.fabs(latvals - latitude).argmin()
    depth = depthvals[latidx, longidx]
    return depth, {"longitude": longvals[longidx], "latitude": latvals[latidx]}


def get_dvalue(longitude, latitude):
    """
    Return the gradient of the depth from the closest longitude, latitude in etopo1

    Args:
        longitude : degrees east
        latitude : degrees north
    """
    fetch_values()
    assert (longvals.min() <= longitude <= longvals.max()) and (
        latvals.min() <= latitude <= latvals.max()
    )
    longidx = np.fabs(longvals - longitude).argmin()
    latidx = np.fabs(latvals - latitude).argmin()
    d_depth = derivative_depthvals[latidx, longidx]
    return d_depth, {"longitude": longvals[longidx], "latitude": latvals[latidx]}


def is_land(long_lat):
    # This is_land is pretty long,
    # prefer using the woa.is_land function
    long0, lat0 = long_lat
    return get_value(long0, lat0) >= 0
