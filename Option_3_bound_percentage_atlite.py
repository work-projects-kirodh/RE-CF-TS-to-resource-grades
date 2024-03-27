"""
Purpose: Returns the averaged capacity factors and saves the netcdf file into the assets folder. Needed for the user
    comparison between the atlite and world atlas datasets.

Author: Kirodh Boodhraj
"""
import numpy as np
import os
from dotenv import load_dotenv
import copy
import pandas as pd

import Option_Support_Functions as support_functions


# Load variables from the .env file
load_dotenv()

def average_capacity_factors_atlite():
    # average the capacity factors according to time:
    atlite_capacity_factors, atlite_capacity_factors_avg = support_functions.create_average_capacity_factor_file_atlite()
    print("... Averaged atlite capacity factor data.")


    # Option 3: Split tiers according to percentage bounds:
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

    # Find the top % values from the temporal average (sorts out user swapping max and min)
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

    # Generate the tiers:
    bound_tier1 = get_tier_percentage_bound(atlite_capacity_factors[os.environ.get("AVG_ATLITE_LATITUDE_VARIABLE_NAME")].values,atlite_capacity_factors[os.environ.get("AVG_ATLITE_LONGITUDE_VARIABLE_NAME")].values,copy.deepcopy(atlite_capacity_factors),selected_indexes_tier1)
    bound_tier2 = get_tier_percentage_bound(atlite_capacity_factors[os.environ.get("AVG_ATLITE_LATITUDE_VARIABLE_NAME")].values,atlite_capacity_factors[os.environ.get("AVG_ATLITE_LONGITUDE_VARIABLE_NAME")].values,copy.deepcopy(atlite_capacity_factors),selected_indexes_tier2)
    bound_tier3 = get_tier_percentage_bound(atlite_capacity_factors[os.environ.get("AVG_ATLITE_LATITUDE_VARIABLE_NAME")].values,atlite_capacity_factors[os.environ.get("AVG_ATLITE_LONGITUDE_VARIABLE_NAME")].values,copy.deepcopy(atlite_capacity_factors),selected_indexes_tier3)
    bound_tier4 = get_tier_percentage_bound(atlite_capacity_factors[os.environ.get("AVG_ATLITE_LATITUDE_VARIABLE_NAME")].values,atlite_capacity_factors[os.environ.get("AVG_ATLITE_LONGITUDE_VARIABLE_NAME")].values,copy.deepcopy(atlite_capacity_factors),selected_indexes_tier4)
    bound_tier5 = get_tier_percentage_bound(atlite_capacity_factors[os.environ.get("AVG_ATLITE_LATITUDE_VARIABLE_NAME")].values,atlite_capacity_factors[os.environ.get("AVG_ATLITE_LONGITUDE_VARIABLE_NAME")].values,copy.deepcopy(atlite_capacity_factors),selected_indexes_tier5)
    print(bound_tier1)
    print(bound_tier2)
    print(bound_tier3)
    print(bound_tier4)
    print(bound_tier5)

    # Create a DataFrame
    tier_dataframe_option_3 = pd.DataFrame({
        'tier_1': bound_tier1,
        'tier_2': bound_tier2,
        'tier_3': bound_tier3,
        'tier_4': bound_tier4,
        'tier_5': bound_tier5
    })

    # check if output directories are created
    if not os.path.exists(os.environ.get('OPTION_3_OUTPUT_FOLDER')):
        os.makedirs(os.environ.get('OPTION_3_OUTPUT_FOLDER'))


    # scale capacity factors if required:
    if os.environ.get('SCALE_CAPACITY_FACTORS').lower() == "true":
        tier_dataframe_option_3 = tier_dataframe_option_3/float(os.environ.get("MAXIMUM_CAPACITY"))  # divide by the weightings
        print("\n... Capacity factors were scaled by division of maximum capacity:",os.environ.get("MAXIMUM_CAPACITY"))


    tier_dataframe_option_3.to_csv(os.path.join(os.environ.get('OPTION_3_OUTPUT_FOLDER'),os.environ.get("BOUND_CAPACITY_FACTORS_TIME_SERIES_FILE_3")),index=False)


    print("\nOption_3 completed successfully!")

if __name__ == '__main__':

    average_capacity_factors_atlite()
