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
import os
from typing import Union

# External modules
import getpass
import numpy as np
import xarray as xr
import copernicusmarine
from copernicusmarine.core_functions.models import DEFAULT_SUBSET_METHOD, SubsetMethod


class CMEMS(object):
    # Datasets used for accessing the measurements
    # med-cmcc
    # https://resources.marine.copernicus.eu/product-detail/MEDSEA_MULTIYEAR_PHY_006_004/INFORMATION
    # med-ogs :
    # https://resources.marine.copernicus.eu/product-detail/MEDSEA_MULTIYEAR_BGC_006_008/INFORMATION
    _feature_params = {
        "temperature": {
            "dataset_id": "med-cmcc-tem-rean-d",
            "variable": "thetao",
            "slice_mode": "lon-lat",
            "has_depth": True,
            "date_limit": datetime.datetime.strptime("01-01-1987", "%d-%m-%Y"),
        },
        "salinity": {
            "dataset_id": "med-cmcc-sal-rean-d",
            "variable": "so",
            "slice_mode": "lon-lat",
            "has_depth": True,
            "date_limit": datetime.datetime.strptime("01-01-1987", "%d-%m-%Y"),
        },
        "eastward-water-velocity": {
            "dataset_id": "med-cmcc-cur-rean-d",
            "variable": "uo",
            "slice_mode": "lon-lat",
            "has_depth": True,
            "date_limit": datetime.datetime.strptime("01-01-1987", "%d-%m-%Y"),
        },
        "northward-water-velocity": {
            "dataset_id": "med-cmcc-cur-rean-d",
            "variable": "vo",
            "slice_mode": "lon-lat",
            "has_depth": True,
            "date_limit": datetime.datetime.strptime("01-01-1987", "%d-%m-%Y"),
        },
        "mixed-layer-thickness": {
            "dataset_id": "med-cmcc-mld-rean-d",
            "variable": "mlotst",
            "slice_mode": "lon-lat",
            "has_depth": False,
            "date_limit": datetime.datetime.strptime("01-01-1987", "%d-%m-%Y"),
        },
        "sea-surface-above-geoid": {
            "dataset_id": "med-cmcc-ssh-rean-d",
            "variable": "zos",
            "slice_mode": "lon-lat",
            "has_depth": False,
            "date_limit": datetime.datetime.strptime("01-01-1987", "%d-%m-%Y"),
        },
        "phytoplankton-carbon-biomass": {
            "dataset_id": "med-ogs-pft-rean-d",
            "variable": "phyc",
            "slice_mode": "longitude-latitude",
            "has_depth": True,
            "date_limit": datetime.datetime.strptime("01-01-1999", "%d-%m-%Y"),
        },
        "chlorophyl-a": {
            "dataset_id": "med-ogs-pft-rean-d",
            "variable": "chl",
            "slice_mode": "longitude-latitude",
            "has_depth": True,
            "date_limit": datetime.datetime.strptime("01-01-1999", "%d-%m-%Y"),
        },
        "nitrate": {
            "dataset_id": "med-ogs-nut-rean-d",
            "variable": "no3",
            "slice_mode": "longitude-latitude",
            "has_depth": True,
            "date_limit": datetime.datetime.strptime("01-01-1999", "%d-%m-%Y"),
        },
        "phosphate": {
            "dataset_id": "med-ogs-nut-rean-d",
            "variable": "po4",
            "slice_mode": "longitude-latitude",
            "has_depth": True,
            "date_limit": datetime.datetime.strptime("01-01-1999", "%d-%m-%Y"),
        },
        "ammonium": {
            "dataset_id": "med-ogs-nut-rean-d",
            "variable": "nh4",
            "slice_mode": "longitude-latitude",
            "has_depth": True,
            "date_limit": datetime.datetime.strptime("01-01-1999", "%d-%m-%Y"),
        },
        "net-primary-production": {
            "dataset_id": "med-ogs-bio-rean-d",
            "variable": "nppv",
            "slice_mode": "longitude-latitude",
            "has_depth": True,
            "date_limit": datetime.datetime.strptime("01-01-1999", "%d-%m-%Y"),
        },
        "oxygen": {
            "dataset_id": "med-ogs-bio-rean-d",
            "variable": "o2",
            "slice_mode": "longitude-latitude",
            "has_depth": True,
            "date_limit": datetime.datetime.strptime("01-01-1999", "%d-%m-%Y"),
        },
        "ph": {
            "dataset_id": "med-ogs-car-rean-d",
            "variable": "ph",
            "slice_mode": "longitude-latitude",
            "has_depth": True,
            "date_limit": datetime.datetime.strptime("01-01-1999", "%d-%m-%Y"),
        },
        "dissolved-inorganic-carbon": {
            "dataset_id": "med-ogs-car-rean-d",
            "variable": "dissic",
            "slice_mode": "longitude-latitude",
            "has_depth": True,
            "date_limit": datetime.datetime.strptime("01-01-1999", "%d-%m-%Y"),
        },
        "alkalinity": {
            "dataset_id": "med-ogs-car-rean-d",
            "variable": "talk",
            "slice_mode": "longitude-latitude",
            "has_depth": True,
            "date_limit": datetime.datetime.strptime("01-01-1999", "%d-%m-%Y"),
        },
        "surface-partial-pressure-co2": {
            "dataset_id": "med-ogs-co2-rean-d",
            "variable": "spco2",
            "slice_mode": "longitude-latitude",
            "has_depth": False,
            "date_limit": datetime.datetime.strptime("01-01-1999", "%d-%m-%Y"),
        },
        "surface-co2-flux": {
            "dataset_id": "med-ogs-co2-rean-d",
            "variable": "fpco2",
            "slice_mode": "longitude-latitude",
            "has_depth": False,
            "date_limit": datetime.datetime.strptime("01-01-1999", "%d-%m-%Y"),
        },
    }

    def __init__(self, num_retries=10):
        # https://help.marine.copernicus.eu/en/articles/8287609-copernicus-marine-toolbox-api-open-a-dataset-or-read-a-dataframe-remotely
        # Copernicus Marine Toolbox API - Open a dataset or read a dataframe remotely
        username = os.getenv("CMEMS_USERNAME")
        if not username:
            logging.warning("Undefined environment variable CMEMS_USERNAME")
            username = input("Please provide the login for accessing CMEMS : ")
        password = os.getenv("CMEMS_PASSWORD")
        if not password:
            logging.warning("Undefined environment variable CMEMS_PASSWORD")
            password = getpass.getpass(
                "Please provide the password for accessing CMEMS : "
            )

        logged_in = copernicusmarine.login(
            username=username, password=password, overwrite_configuration_file=True
        )
        if not logged_in:
            raise RuntimeError("Login to cmems unsucessfull, aborting...")

        logging.info("Connection to cmems successfull")

    def get_value(
        self,
        date: Union[datetime.datetime, tuple[datetime.datetime, datetime.datetime]],
        long_lat: tuple[float, float],
        depth: Union[float, tuple[float, float]],
        what: str,
        reduction=None,
    ):
        def f_slice(dataset_id, variable, date, long_lat, depth, has_depth):
            subset_method = DEFAULT_SUBSET_METHOD

            params = {}
            if isinstance(long_lat[0], tuple):
                params["minimum_longitude"] = long_lat[0][0]
                params["maximum_longitude"] = long_lat[0][1]
            else:
                params["minimum_longitude"] = long_lat[0]
                params["maximum_longitude"] = long_lat[0]
            if isinstance(long_lat[1], tuple):
                params["minimum_latitude"] = long_lat[1][0]
                params["maximum_latitude"] = long_lat[1][1]
            else:
                params["minimum_latitude"] = long_lat[1]
                params["maximum_latitude"] = long_lat[1]

            if has_depth:
                if isinstance(depth, tuple):
                    params["minimum_depth"] = depth[0]
                    params["maximum_depth"] = depth[1]
                else:
                    params["minimum_depth"] = depth
                    params["maximum_depth"] = depth

            if isinstance(date, tuple):
                params["start_datetime"] = date[0]
                params["end_datetime"] = date[1]
            else:
                params["start_datetime"] = date
                params["end_datetime"] = date

            # Drop duplicated indices
            # This happens for example with oxygen, nppv, ph, alkalinity, dissic
            # ds = ds.drop_duplicates(dim=...)

            df_values = copernicusmarine.read_dataframe(
                dataset_id=dataset_id,
                variables=[variable],
                subset_method=subset_method,
                **params,
            )

            # The noslice coordinates will appear as columns
            # we reset the index to get all the dimensions as columns
            df_values.reset_index(inplace=True)

            if not has_depth:
                # In this case, where a dataset cannot be indexed by depth
                # we simply ignore the depth and fill in the value we got
                # possibly at the surface
                df_values["depth"] = depth

            # before defining our own expected ordering of the dimensions
            df_values.set_index(
                ["time", "longitude", "latitude", "depth"], inplace=True
            )

            # Ensure we always have longitude and latitude for spatial
            # coordinates
            df_values.index.rename(
                ["time", "longitude", "latitude", "depth"], inplace=True
            )
            if reduction == "mean":
                result = df_values.mean().item()
            else:
                result = df_values

            time_coords = np.unique(df_values.index.get_level_values("time").to_numpy())
            longitude_coords = np.unique(
                df_values.index.get_level_values("longitude").to_numpy()
            )
            latitude_coords = np.unique(
                df_values.index.get_level_values("latitude").to_numpy()
            )
            depth_coords = np.unique(
                df_values.index.get_level_values("depth").to_numpy()
            )

            selected_coordinates = {
                "time": time_coords,
                "longitude": longitude_coords,
                "latitude": latitude_coords,
                "depth": depth_coords if has_depth else float("nan"),
            }
            return result, selected_coordinates

        # Get access to the datastore
        if what in CMEMS._feature_params.keys():
            params = CMEMS._feature_params[what]

            # From 1987 to present
            if (isinstance(date, tuple) and date[0] < params["date_limit"]) or (
                not isinstance(date, tuple) and date < params["date_limit"]
            ):
                raise ValueError(f"Cannot get {what} before {params['date_limit']}")
            # datastore = self.fetch(params["prefix"], params["dataset"])
            logging.info(f"Slicing for {params['variable']}")

            return f_slice(
                params["dataset_id"],
                params["variable"],
                date,
                long_lat,
                depth,
                params["has_depth"],
            )
        else:
            raise ValueError(
                f"Does not know which dataset to download for the key {what}"
            )
