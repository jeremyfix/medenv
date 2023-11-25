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

# Local imports
import medenv

logging.basicConfig(level=logging.DEBUG)

cmems = medenv.cmems.CMEMS()

date = datetime.datetime(year=2020, month=7, day=31)
long0, lat0 = -2.95, 35.32
depth = 8.3
temperature, info_temperature = cmems.get_value(
    date, (long0, lat0), depth, "temperature"
)
salinity, info_salinity = cmems.get_value(date, (long0, lat0), depth, "salinity")

logging.info(
    f"For the location {long0, lat0}, at depth {depth} m., on the {date} :\n - Temperature : {temperature}°C from {info_temperature}\n - Salinity : {salinity} from {info_salinity}"
)
