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
import xarray as xr
import copernicusmarine


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
        self.datastores = {}

    def fetch(self, prefix_dataset, dataset):
        if dataset not in self.datastores:
            logging.info(f"Opening the connection to the dataset {dataset}")
            url = f"https://{prefix_dataset}.cmems-du.eu/thredds/dodsC/{dataset}"
            retries = 0
            while True:
                try:
                    logging.debug(f"Opening {url}")
                    datastream = open_url(
                        url, session=self.session, user_charset="utf-8"
                    )
                    logging.debug(f"Opened with datatype {type(datastream)}")
                    data_store = xr.backends.PydapDataStore(datastream)
                    break
                except:
                    logging.warning(
                        f"Failure, one more retry, {self.num_retries-retries} remaining"
                    )
                    retries += 1
                    if retries >= self.num_retries:
                        raise RuntimeError("Cannot successfully access the dataset")
            self.datastores[dataset] = xr.open_dataset(data_store)
            logging.debug(
                f"The downloaded datastore for {dataset} is : \n {self.datastores[dataset]} "
            )
        return self.datastores[dataset]

    def get_value(
        self,
        date: Union[datetime.datetime, tuple[datetime.datetime, datetime.datetime]],
        long_lat: tuple[float, float],
        depth: Union[float, tuple[float, float]],
        what: str,
        reduction=None,
    ):
        def f_slice(ds, mode, date, long_lat, depth, has_depth):
            if mode == "lon-lat":
                key_lon = "lon"
                key_lat = "lat"
            else:
                key_lon = "longitude"
                key_lat = "latitude"

            slice_coords_definition = {}
            noslice_coords_definition = {
                "method": "nearest",
            }

            if isinstance(long_lat[0], tuple):
                slice_coords_definition[key_lon] = slice(*(long_lat[0]))
            else:
                noslice_coords_definition[key_lon] = long_lat[0]

            if isinstance(long_lat[1], tuple):
                slice_coords_definition[key_lat] = slice(*(long_lat[1]))
            else:
                noslice_coords_definition[key_lat] = long_lat[1]

            if has_depth:
                if isinstance(depth, tuple):
                    slice_coords_definition["depth"] = slice(depth[0], depth[1])
                else:
                    noslice_coords_definition["depth"] = depth

            if isinstance(date, tuple):
                slice_coords_definition["time"] = slice(date[0], date[1])
            else:
                noslice_coords_definition["time"] = date

            # Drop duplicated indices
            # This happens for example with oxygen, nppv, ph, alkalinity, dissic
            ds = ds.drop_duplicates(dim=...)

            # Select the slicing and no slicing from the dataset
            values = ds.sel(**slice_coords_definition)
            values = values.sel(**noslice_coords_definition)

            # Convert the result into a dataframe
            df_values = values.to_dataframe()

            # The noslice coordinates will appear as columns
            # we reset the index to get all the dimensions as columns
            df_values.reset_index(inplace=True)

            if not has_depth:
                # In this case, where a dataset cannot be indexed by depth
                # we simply ignore the depth and fill in the value we got
                # possibly at the surface
                df_values["depth"] = depth

            # before defining our own expected ordering of the dimensions
            df_values.set_index(["time", key_lon, key_lat, "depth"], inplace=True)

            # Ensure we always have longitude and latitude for spatial
            # coordinates
            df_values.index.rename(
                ["time", "longitude", "latitude", "depth"], inplace=True
            )
            if reduction == "mean":
                result = df_values.mean().item()
            else:
                result = df_values

            selected_coordinates = {
                "time": values.coords["time"].to_numpy(),
                key_lon: values.coords[key_lon].to_numpy(),
                key_lat: values.coords[key_lat].to_numpy(),
                "depth": values.coords["depth"].to_numpy()
                if has_depth
                else float("nan"),
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
            datastore = self.fetch(params["prefix"], params["dataset"])
            logging.info(f"Slicing for {params['field']}")

            return f_slice(
                datastore[params["field"]],
                params["slice_mode"],
                date,
                long_lat,
                depth,
                params["has_depth"],
            )
        else:
            raise ValueError(
                f"Does not know which dataset to download for the key {what}"
            )
