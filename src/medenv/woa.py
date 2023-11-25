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

# The data are provided by the NOAA
# see : https://www.ncei.noaa.gov/products/world-ocean-atlas

# Standard imports
import logging
from datetime import datetime

# External imports
import pandas as pd

# Local imports
from medenv import utils


# Available measures from WOA 2018
# Temperature (t), Salinity (s), Oxygen (o), Nitrate(n), Phosphate(p), Silicate(i)
# For mixed layer depth, Density, Conductivity, Mixed Layer Depth, Dissolved Oxygen, Percent Oxygen Saturation, Apprent Oxygen utilization, see : https://www.ncei.noaa.gov/access/world-ocean-atlas-2018/
_WOA_BASE_URL = "https://www.ncei.noaa.gov/data/oceans/woa/WOA18/DATA/"
# temperature/csv/8594/1.00/woa18_8594_t01mn01.csv.gz

_WOA_LAND_SEA_URL = (
    "https://www.ncei.noaa.gov/data/oceans/woa/WOA18/MASKS/landsea_04.msk"
)

_AVAILABLE_RESOLUTIONS = [5.0, 1.0, 0.25]
_DEFAULT_RESOLUTION = 1.0
_AVAILABLE_MEASURES = {
    "temperature": "t",
    "salinity": "s",
    # "oxygen": "o",  # Not yet released for WOA2018 [2022]
    # "nitrate": "t",
    # "phosphate": "p",
    # "silicate": "i",
}


def get_period(year):
    if year < 1955 or year > 2017:
        raise ValueError(
            f"WOA2018 does not provide measures for year {year}. The available years are in 1955-2017"
        )
    elif year <= 1964:
        return "5564"
    elif year <= 1974:
        return "6574"
    elif year <= 1984:
        return "7584"
    elif year <= 1994:
        return "8594"
    elif year <= 2004:
        return "95A4"
    elif year <= 2017:
        return "A5B7"


def get_grid_resolution_id(resolution):
    if resolution == 0.25:
        return "04"
    elif resolution == 1.0:
        return "01"
    elif resolution == 5.0:
        return "5d"
    else:
        raise ValueError(
            f"Resolution {resolution} not supported by WOA. Possible resolutions are 0.25, 1.0 or 5.0"
        )


def get_statistics_id(statistics):
    dstatistics = {
        "Objectively analyzed climatology": "an",
        "Statistical mean": "mn",  #
        "Number of observations": "dd",
        "Seasonal climatology": "ma",  # or monthly climatology
        "Standard deviation": "sd",
        "Standard error": "se",  # Standard deviation from statistical mean
        "Statistical mean moa": "oa",  # Statistical mean minus objectively analyzed climatology
        "Number of mean values": "gp",  # Number of mean values within radius of influence
    }
    return dstatistics[statistics]


def build_url(date, what, resolution):
    # The datafile naming convention follows :
    # woa18_[DECA]_[v][tp][ft][gr].[form_end]
    period = get_period(date.year)
    month = date.month
    whatkey = _AVAILABLE_MEASURES[what]
    statistics = get_statistics_id("Objectively analyzed climatology")
    grid_resolution = get_grid_resolution_id(resolution)
    assert resolution in _AVAILABLE_RESOLUTIONS
    return f"{_WOA_BASE_URL}/{what}/csv/{period}/{resolution:.02f}/woa18_{period}_{whatkey}{month:02d}{statistics}{grid_resolution}.csv.gz"


def read_csv(filepath):
    with open(filepath, "r") as f:
        f.readline()  # skip the header
        # The header containings the depths are
        # given like :
        #   #COMMA SEPARATED LATITUDE, LONGITUDE, AND VALUES AT DEPTHS (M):0,5,10, ...
        header_depth = f.readline()
        depths = list(map(float, header_depth.split(":")[1].split(",")))
        data = pd.read_csv(
            f, encoding="iso-8859-1", names=["latitude", "longitude"] + depths
        )
        return data


def fetch_values(date, what, resolution=_DEFAULT_RESOLUTION):
    """
    (longitude, latitude) :(degrees east, degrees north)
    date: datetime
    what: str in ['SST', 'Tmax-min', 'Salinity', 'MLD', ...]
    resolution: 5.00, 1.00 or 0.25
    """

    url = build_url(date, what, resolution)
    filename = f"r{resolution}-" + url.split("/")[-1][:-3]  # file.csv
    filepath = utils.download_and_extract(url, "gzip", filename)
    data = read_csv(filepath)
    return data


def get_value(long_lat, depth, what, resolution=_DEFAULT_RESOLUTION):
    data = fetch_values(datetime(year=2016, month=1, day=1), what, resolution)
    long0, lat0 = long_lat
    idx = (
        abs(data["longitude"] - long0) ** 2 + abs(data["latitude"] - lat0) ** 2
    ).idxmin()
    depth_idx = abs(data.columns[2:] - depth).argmin()
    # TODO: warn if the depth_idx is the maximal depth ?? maybe far from the request ?
    return data.loc[idx].iloc[depth_idx + 2]


def fetch_landsea():
    filename = "land_sea.msk"
    filename = utils._BASEDIR / filename
    filepath = utils.download_url(_WOA_LAND_SEA_URL, filename)
    data = pd.read_csv(
        filepath,
        encoding="iso-8859-1",
        names=["latitude", "longitude", "BottomStdLevel"],
        skiprows=2,
    )
    return data


def is_land(long_lat):
    data = fetch_landsea()
    long0, lat0 = long_lat
    idx = (
        abs(data["longitude"] - long0) ** 2 + abs(data["latitude"] - lat0) ** 2
    ).idxmin()
    return data.loc[idx].iloc[2] == 1  # 1 for land / 0 for sea
