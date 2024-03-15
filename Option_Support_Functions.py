"""
Purpose: Support functions for generating tiers.

Author: Kirodh Boodhraj
"""
import os
import xarray as xr
import numpy as np
import temporary_data as temp_data
from dotenv import load_dotenv

# Load variables from the .env file
load_dotenv()

def create_average_capacity_factor_file_atlite():
    # TODO: read in the capacity factors after running WP3 codes:
    # xr.open_dataset(os.environ.get('ATLITE_CAPACITY_FACTORS_FILE_LOCATION'))
    ## use temp data for now:
    atlite_capacity_factors = temp_data.create_dataset()
    print("... Opened atlite capacity factor data.")

    # average the capacity factors according to time:
    atlite_capacity_factors_avg = atlite_capacity_factors[os.environ.get("DATA_VARIABLE_NAME")].mean(dim=os.environ.get("TIME_VARIABLE_NAME"))
    print("... Averaged atlite capacity factor data.")

    # save file to assets folder:
    atlite_capacity_factors_avg.to_netcdf(os.environ.get("AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION"))
    print("... Saved average atlite capacity factor data.")

    return atlite_capacity_factors, atlite_capacity_factors_avg


def read_wind_atlas_data_full():
    # get down scaling resolution of wind atlas netcdf i.e. number of points to skip for lat lon values in array, to make things render faster
    wind_atlas_resolution_reduction = int(os.environ.get("WIND_ATLAS_RESOLUTION_REDUCTION"))
    # open wind atlas netcdf
    wind_atlas_netcdf = xr.open_dataset(os.environ.get("WIND_ATLAS_CAPACITY_FACTORS_HEATMAP_FILE_LOCATION"))

    # # Select every wind_atlas_resolution_reduction latitude and longitude along with capacity_factor
    # capacity_factor_subset = wind_atlas_netcdf.sel(
    #     lat=wind_atlas_netcdf.lat.values[::wind_atlas_resolution_reduction],
    #     lon=wind_atlas_netcdf.lon.values[::wind_atlas_resolution_reduction])

    # Access the capacity_factor variable from the subset
    latitude_wa = wind_atlas_netcdf[os.environ.get("WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME")].values.astype(float)
    longitude_wa = wind_atlas_netcdf[os.environ.get("WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME")].values.astype(float)
    values_wa = wind_atlas_netcdf[os.environ.get("WIND_ATLAS_HEATMAP_DATA_VARIABLE_NAME")].values.astype(float)
    # values_wa[np.isnan(values_wa)] = 0.0  # Replace NaN with 0.0, you can choose a different value if needed
    # lon_wa, lat_wa = np.meshgrid(longitude_wa, latitude_wa)
    return latitude_wa,longitude_wa,values_wa


def read_wind_atlas_data_reduced():
    # get down scaling resolution of wind atlas netcdf i.e. number of points to skip for lat lon values in array, to make things render faster
    wind_atlas_resolution_reduction = int(os.environ.get("WIND_ATLAS_RESOLUTION_REDUCTION"))
    # open wind atlas netcdf
    wind_atlas_netcdf = xr.open_dataset(os.environ.get("WIND_ATLAS_CAPACITY_FACTORS_HEATMAP_FILE_LOCATION"))

    # Select every wind_atlas_resolution_reduction latitude and longitude along with capacity_factor
    capacity_factor_subset = wind_atlas_netcdf.sel(
        lat=wind_atlas_netcdf.lat.values[::wind_atlas_resolution_reduction],
        lon=wind_atlas_netcdf.lon.values[::wind_atlas_resolution_reduction])

    # Access the capacity_factor variable from the subset
    latitude_wa = capacity_factor_subset[os.environ.get("WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME")].values.astype(float)
    longitude_wa = capacity_factor_subset[os.environ.get("WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME")].values.astype(float)
    values_wa = capacity_factor_subset[os.environ.get("WIND_ATLAS_HEATMAP_DATA_VARIABLE_NAME")].values.astype(float)
    # values_wa[np.isnan(values_wa)] = 0.0  # Replace NaN with 0.0, you can choose a different value if needed
    # lon_wa, lat_wa = np.meshgrid(longitude_wa, latitude_wa)

    return latitude_wa,longitude_wa,values_wa



