"""
Purpose: Returns random data as a temporary measure for now.

Author: Kirodh Boodhraj
"""

import numpy as np
import pandas as pd
import xarray as xr
import os
from dotenv import load_dotenv

# Load variables from the .env file
load_dotenv()

# Function to generate random data
def generate_random_data(latitudes, longitudes):
    maximum_capacity = os.environ.get("MAXIMUM_CAPACITY") # MW
    return np.random.rand(len(latitudes), len(longitudes)),maximum_capacity

def create_dataset():
    # Step 1: Create hourly date times in a Pandas series
    hourly_date_times = pd.date_range(start=os.environ.get("START_DATE"), end=os.environ.get("END_DATE"), freq='H')


    """ temporary fix start """
    # Step 2: Create equally spaced intervals of 0.1 degrees between latitudes and longitudes
    latitude_intervals = np.arange(float(os.environ.get("LATITUDE_BOTTOM")), float(os.environ.get("LATITUDE_TOP")), 0.1)
    longitude_intervals = np.arange(float(os.environ.get("LONGITUDE_LEFT")), float(os.environ.get("LONGITUDE_RIGHT")), 0.1)

    # Step 3: Create an empty Xarray dataset
    atlite_capacity_factors = xr.Dataset(
        {
            'capacity_factors': (['time', 'latitude', 'longitude'], np.zeros((len(hourly_date_times), len(latitude_intervals), len(longitude_intervals))))
        },
        coords={
            'time': hourly_date_times,
            'latitude': latitude_intervals,
            'longitude': longitude_intervals
        }
    )
    """ temporary fix end """

    # Step 4: Loop through each hourly timestep and generate random data
    for i, time in enumerate(hourly_date_times):
        # print("At timestep: ",i)
        #### Step 1:
        # TODO: Link to Nicolene's algorithm here
        """ temporary fix """
        capacity_factors, maximum_capacity = generate_random_data(latitude_intervals, longitude_intervals)
        atlite_capacity_factors[os.environ.get('DATA_VARIABLE_NAME')][i, :, :] = capacity_factors
        """ temporary fix """

    # print(atlite_capacity_factors["latitude"],atlite_capacity_factors["longitude"])

    return atlite_capacity_factors