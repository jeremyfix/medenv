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
from datetime import datetime
import functools
from typing import Union

logging.getLogger("medenv").addHandler(logging.NullHandler())


# Local imports
from medenv import etopo
from medenv import woa
from medenv import cmems


class Fetcher:
    _available_features = [
        "bathymetry",
        "sea-surface-temperature",
        "sea-surface-salinity",
    ] + list(cmems.CMEMS._feature_params.keys())

    def __init__(self, features, reduction=None):
        self.features = features
        self.getters = {}
        self.cmems_getter = None
        print(len(Fetcher._available_features))
        for f in features:
            if f not in Fetcher._available_features:
                raise ValueError(
                    f"The feature {f} is not in the available features {Fetcher._available_features}"
                )

            if f in list(cmems.CMEMS._feature_params.keys()):
                if self.cmems_getter is None:
                    self.cmems_getter = cmems.CMEMS()
                self.getters[f] = functools.partial(
                    self.cmems_getter.get_value, what=f, reduction=reduction
                )
            elif f == "bathymetry":
                self.getters[f] = lambda date, long_lat, depth: etopo.get_value(
                    long_lat[0], long_lat[1]
                )
            elif f == "sea-surface-temperature":
                if self.cmems_getter is None:
                    self.cmems_getter = cmems.CMEMS()
                self.getters[
                    f
                ] = lambda date, long_lat, depth: self.cmems_getter.get_value(
                    date=date,
                    long_lat=long_lat,
                    depth=0,
                    what="temperature",
                    reduction=reduction,
                )
            elif f == "sea-surface-salinity":
                if self.cmems_getter is None:
                    self.cmems_getter = cmems.CMEMS()
                self.getters[
                    f
                ] = lambda date, long_lat, depth: self.cmems_getter.get_value(
                    date=date,
                    long_lat=long_lat,
                    depth=0,
                    what="salinity",
                    reduction=reduction,
                )

    def get_values(
        self,
        date: Union[datetime, tuple[datetime, datetime]],
        long_lat: tuple[float, float],
        depth: Union[float, tuple[float, float]],
        reduction=None,
    ):
        values, infos = {}, {}
        for f in self.features:
            logging.info(f"Fetching {f} ")
            values[f], infos[f] = self.getters[f](date, long_lat, depth)
        return values, infos
