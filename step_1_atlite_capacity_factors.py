"""
Purpose: Returns the averaged capacity factors and saves the netcdf file into the assets folder. Needed for the user
    comparison between the atlite and world atlas datasets.

Author: Kirodh Boodhraj
"""

import os
import xarray as xr
import temporary_data as temp_data
from dotenv import load_dotenv

# Load variables from the .env file
load_dotenv()


def average_capacity_factors_atlite():
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

    print("Please run step_2____.py!")

if __name__ == '__main__':

    average_capacity_factors_atlite()
