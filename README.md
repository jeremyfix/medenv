# Environmental measures from mediterranean see

This package provides several utilities for requesting environmental measures in the Mediterrannean see. 

## Installation

In order to install the package, since it is not yet available in pypi, you can :

	python3 -m pip install git+https://github.com/jeremyfix/medenv.git

You can also install it by cloning the repository
	
	git clone https://github.com/jeremyfix/medenv.git
	python3 -m venv venv
	source venv/bin/activate
	python -m pip install medenv

## Usage

Check the examples in the `examples/` directory, but basically, grabbing environmental variables require a `Fetcher` to which you specify which features you want to grab and then provides `(latitude, longitude, time, depth)` requests: 

``` python
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

fetcher = medenv.Fetcher(features, reduction="mean")

date = datetime.datetime(year=2012, month=9, day=22, hour=14)
long, lat = 13.63, 43.55
tol_spatial = 0.2
long0 = (long - tol_spatial / 2, long + tol_spatial / 2)
lat0 = (lat - tol_spatial / 2, lat + tol_spatial / 2)
depth = 6

values, info_values = fetcher.get_values(date, (long0, lat0), depth)
```

The request accepts a range for the longitude/latitude and a single value for the date and depth. For both the date and depth, the fetcher will grab the closest values.
