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


    # Use boolean indexing to select the desired indexes
    selected_indexes = atlite_capacity_factors_avg.where(atlite_capacity_factors_avg>top_percentage)#, drop=True)

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

    # get the final tier and save it
    tiers_raw_df['average_tier_final'] = tiers_raw_df.mean(axis=1)
    tiers_raw_df.to_csv(os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS_TIME_SERIES_FILE"))
    lat_lon_df.to_csv(os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE"))

    print("... Tier files for top "+os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS")+" capacity factors created:")
    print("...... Location file located in: "+os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE"))
    print("...... Tier file located in: "+os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS_TIME_SERIES_FILE"))
    print("... Note that averaged tier is in average_tier_final column.")


    # Option 1A: Split tiers according to percentage bounds:
    def get_tier_percentage_bound(lats,longs,atlite_data,selected_data):
        # count as the values get added on to take the average at the end
        number_columns_in_tier = 0
        # skeleton to hold the values
        cumulative_average_values = np.zeros((len(atlite_data[os.environ.get("DATA_VARIABLE_NAME")].values[:,0,0])))

        # loop through and find if nan or data
        for lat in range(len(lats)):
            for lon in range(len(longs)):
                value = selected_data.data[lat][lon]
                if np.isnan(value):
                    continue
                else:
                    # print("Found values!",cumulative_average_values)
                    # Add the new column to the skeleton column
                    cumulative_average_values += atlite_data[os.environ.get("DATA_VARIABLE_NAME")].values[:, lat, lon]
                    number_columns_in_tier += 1

        # take the average
        print("... A tier was created.")
        return cumulative_average_values/number_columns_in_tier

    # Convert the PERCENT_UPPER_TIER1_CAPACITY_FACTORS variable to a list of floats
    percent_upper_tier1_capacity_factors = list(map(float, os.environ.get("PERCENT_UPPER_TIER1_CAPACITY_FACTORS").split(',')))
    percent_upper_tier2_capacity_factors = list(map(float, os.environ.get("PERCENT_UPPER_TIER2_CAPACITY_FACTORS").split(',')))
    percent_upper_tier3_capacity_factors = list(map(float, os.environ.get("PERCENT_UPPER_TIER3_CAPACITY_FACTORS").split(',')))
    percent_upper_tier4_capacity_factors = list(map(float, os.environ.get("PERCENT_UPPER_TIER4_CAPACITY_FACTORS").split(',')))
    percent_upper_tier5_capacity_factors = list(map(float, os.environ.get("PERCENT_UPPER_TIER5_CAPACITY_FACTORS").split(',')))

    # Find the top % values from the temporal average
    upper_percentile_tier1 = 1.0 - min(percent_upper_tier1_capacity_factors) / 100.0
    upper_percentile_tier2 = 1.0 - min(percent_upper_tier2_capacity_factors) / 100.0
    upper_percentile_tier3 = 1.0 - min(percent_upper_tier3_capacity_factors) / 100.0
    upper_percentile_tier4 = 1.0 - min(percent_upper_tier4_capacity_factors) / 100.0
    upper_percentile_tier5 = 1.0 - min(percent_upper_tier5_capacity_factors) / 100.0

    lower_percentile_tier1 = 1.0 - max(percent_upper_tier1_capacity_factors) / 100.0
    lower_percentile_tier2 = 1.0 - max(percent_upper_tier2_capacity_factors) / 100.0
    lower_percentile_tier3 = 1.0 - max(percent_upper_tier3_capacity_factors) / 100.0
    lower_percentile_tier4 = 1.0 - max(percent_upper_tier4_capacity_factors) / 100.0
    lower_percentile_tier5 = 1.0 - max(percent_upper_tier5_capacity_factors) / 100.0

    # Find the values between the specified quantiles
    bounds_tier1 = copy.deepcopy(atlite_capacity_factors_avg).stack(z=(os.environ.get("AVG_ATLITE_LATITUDE_VARIABLE_NAME"), os.environ.get("AVG_ATLITE_LONGITUDE_VARIABLE_NAME"))).quantile([lower_percentile_tier1, upper_percentile_tier1], dim='z')
    bounds_tier2 = copy.deepcopy(atlite_capacity_factors_avg).stack(z=(os.environ.get("AVG_ATLITE_LATITUDE_VARIABLE_NAME"), os.environ.get("AVG_ATLITE_LONGITUDE_VARIABLE_NAME"))).quantile([lower_percentile_tier2, upper_percentile_tier2], dim='z')
    bounds_tier3 = copy.deepcopy(atlite_capacity_factors_avg).stack(z=(os.environ.get("AVG_ATLITE_LATITUDE_VARIABLE_NAME"), os.environ.get("AVG_ATLITE_LONGITUDE_VARIABLE_NAME"))).quantile([lower_percentile_tier3, upper_percentile_tier3], dim='z')
    bounds_tier4 = copy.deepcopy(atlite_capacity_factors_avg).stack(z=(os.environ.get("AVG_ATLITE_LATITUDE_VARIABLE_NAME"), os.environ.get("AVG_ATLITE_LONGITUDE_VARIABLE_NAME"))).quantile([lower_percentile_tier4, upper_percentile_tier4], dim='z')
    bounds_tier5 = copy.deepcopy(atlite_capacity_factors_avg).stack(z=(os.environ.get("AVG_ATLITE_LATITUDE_VARIABLE_NAME"), os.environ.get("AVG_ATLITE_LONGITUDE_VARIABLE_NAME"))).quantile([lower_percentile_tier5, upper_percentile_tier5], dim='z')

    # extract the bounds:
    top_bound_tier1 = bounds_tier1.values[1]
    top_bound_tier2 = bounds_tier2.values[1]
    top_bound_tier3 = bounds_tier3.values[1]
    top_bound_tier4 = bounds_tier4.values[1]
    top_bound_tier5 = bounds_tier5.values[1]

    bottom_bound_tier1 = bounds_tier1.values[0]
    bottom_bound_tier2 = bounds_tier2.values[0]
    bottom_bound_tier3 = bounds_tier3.values[0]
    bottom_bound_tier4 = bounds_tier4.values[0]
    bottom_bound_tier5 = bounds_tier5.values[0]

    # Use boolean indexing to select the desired indexes
    selected_indexes_tier1 = atlite_capacity_factors_avg.where((atlite_capacity_factors_avg>bottom_bound_tier1) & (atlite_capacity_factors_avg<top_bound_tier1))#, drop=True)

    selected_indexes_tier2 = atlite_capacity_factors_avg.where((atlite_capacity_factors_avg>bottom_bound_tier2) & (atlite_capacity_factors_avg<top_bound_tier2))#, drop=True)
    selected_indexes_tier3 = atlite_capacity_factors_avg.where((atlite_capacity_factors_avg>bottom_bound_tier3) & (atlite_capacity_factors_avg<top_bound_tier3))#, drop=True)
    selected_indexes_tier4 = atlite_capacity_factors_avg.where((atlite_capacity_factors_avg>bottom_bound_tier4) & (atlite_capacity_factors_avg<top_bound_tier4))#, drop=True)
    selected_indexes_tier5 = atlite_capacity_factors_avg.where((atlite_capacity_factors_avg>bottom_bound_tier5) & (atlite_capacity_factors_avg<top_bound_tier5))#, drop=True)

    # Generate the tiers for option 1A:
    bound_tier1 = get_tier_percentage_bound(atlite_capacity_factors["latitude"].values,atlite_capacity_factors["longitude"].values,copy.deepcopy(atlite_capacity_factors),selected_indexes_tier1)
    bound_tier2 = get_tier_percentage_bound(atlite_capacity_factors["latitude"].values,atlite_capacity_factors["longitude"].values,copy.deepcopy(atlite_capacity_factors),selected_indexes_tier2)
    bound_tier3 = get_tier_percentage_bound(atlite_capacity_factors["latitude"].values,atlite_capacity_factors["longitude"].values,copy.deepcopy(atlite_capacity_factors),selected_indexes_tier3)
    bound_tier4 = get_tier_percentage_bound(atlite_capacity_factors["latitude"].values,atlite_capacity_factors["longitude"].values,copy.deepcopy(atlite_capacity_factors),selected_indexes_tier4)
    bound_tier5 = get_tier_percentage_bound(atlite_capacity_factors["latitude"].values,atlite_capacity_factors["longitude"].values,copy.deepcopy(atlite_capacity_factors),selected_indexes_tier5)
    print(bound_tier1)
    print(bound_tier2)
    print(bound_tier3)
    print(bound_tier4)
    print(bound_tier5)

    # Create a DataFrame
    tier_dataframe_option1A = pd.DataFrame({
        'tier_1': bound_tier1,
        'tier_2': bound_tier2,
        'tier_3': bound_tier3,
        'tier_4': bound_tier4,
        'tier_5': bound_tier5
    })

    tier_dataframe_option1A.to_csv(os.environ.get("BOUND_CAPACITY_FACTORS_TIME_SERIES_FILE"),index=False)


    print("Please run step_2____.py!")

if __name__ == '__main__':

    average_capacity_factors_atlite()
