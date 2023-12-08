"""
Purpose: Returns the averaged capacity factors and saves the netcdf file into the assets folder. Needed for the user
    comparison between the atlite and world atlas datasets.

Author: Kirodh Boodhraj
"""
import numpy as np
import os
import xarray as xr
import temporary_data as temp_data
from dotenv import load_dotenv
import copy
import pandas as pd

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

    # TODO:::: save top % capacity factors and generate a time series from that
    print("... Generating time series from top "+os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS")+" capacity factors")
    try:
        check_percentage = float(os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS"))
        if check_percentage < 0:
            ValueError("The percentage is less than 0. Only 0-100 allowed.")
        if check_percentage > 100:
            ValueError("The percentage is larger than 100. Only 0-100 allowed.")
    except Exception as e:
        ValueError("The percentage is not a number. Only 0-100 allowed.")
    # Find the top % values from the temporal average
    top_percentage = copy.deepcopy(atlite_capacity_factors_avg).stack(z=(os.environ.get("AVG_ATLITE_LATITUDE_VARIABLE_NAME"), os.environ.get("AVG_ATLITE_LONGITUDE_VARIABLE_NAME"))).quantile(1.0 - float(os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS"))/100)
    # print("Top",top_percentage.data)
    # print(atlite_capacity_factors_avg)
    # print(atlite_capacity_factors_avg.shape)

    # Use boolean indexing to select the desired indexes
    selected_indexes = atlite_capacity_factors_avg.where(atlite_capacity_factors_avg>top_percentage, drop=True)

    # get lats/lons
    latitudes = selected_indexes[os.environ.get(("AVG_ATLITE_LATITUDE_VARIABLE_NAME"))].values
    longitudes = selected_indexes[os.environ.get(("AVG_ATLITE_LONGITUDE_VARIABLE_NAME"))].values

    # empty shell to store the lats/lons and the data, then average them later
    lat_lon_df = pd.DataFrame(columns=['latitude', 'longitude','average_capacity_factor'])
    tiers_raw_df = pd.DataFrame()

    # loop through and find if nan or data
    for lat in range(len(latitudes)):
        for lon in range(len(longitudes)):
            value = selected_indexes.data[lat][lon]
            if np.isnan(value):
                continue
            else:
                # add data to the data frame
                # lat/lon
                lat_lon_df.loc[len(lat_lon_df)] = [latitudes[lat],longitudes[lon],value]
                # timeseries
                # Determine the next number for the new column name
                next_column_number = len(tiers_raw_df.columns) + 1
                # Create a new column name
                new_column_name = f'pre_tier_{next_column_number}'
                # Add the new column to the DataFrame
                tiers_raw_df[new_column_name] = atlite_capacity_factors[os.environ.get("DATA_VARIABLE_NAME")].values[:,lat,lon]
                # print(value)

    # print(lat_lon_df)
    # print(tiers_raw_df)

    # get the final tier and save it
    tiers_raw_df['average_tier_final'] = tiers_raw_df.mean(axis=1)
    tiers_raw_df.to_csv(os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS_TIME_SERIES_FILE"))
    lat_lon_df.to_csv(os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE"))

    print("... Tier files for top "+os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS")+" capacity factors created:")
    print("...... Location file located in: "+os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE"))
    print("...... Tier file located in: "+os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS_TIME_SERIES_FILE"))
    print("... Note that averaged tier is in average_tier_final column.")




    print("Please run step_2____.py!")

if __name__ == '__main__':

    average_capacity_factors_atlite()
