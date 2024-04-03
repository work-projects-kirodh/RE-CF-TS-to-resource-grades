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
import argparse

import Option_Support_Functions as support_functions

################################
# system args section
################################
# used for running the codes
def parse_arguments():
    parser = argparse.ArgumentParser(description="(Option 3) Script to calculate average capacity factors.")
    parser.add_argument('--ATLITE_DUMMY_DATA', default=None, required=False,help="Boolean to use the dummy Atlite data (True) or not.")
    parser.add_argument('--ATLITE_CAPACITY_FACTORS_FOLDERS', default=None, required=False,help="Folders continaing hourly Atlite data files needing stitching.")
    parser.add_argument('--DUMMY_START_DATE', default=None, required=False, help="Start date.")
    parser.add_argument('--DUMMY_END_DATE', default=None, required=False, help="End date.")
    parser.add_argument('--DUMMY_LATITUDE_BOTTOM', default=None, required=False, help="Latitude bottom.")
    parser.add_argument('--DUMMY_LATITUDE_TOP', default=None, required=False, help="Latitude top.")
    parser.add_argument('--DUMMY_LONGITUDE_LEFT', default=None, required=False, help="Longitude left.")
    parser.add_argument('--DUMMY_LONGITUDE_RIGHT', default=None, required=False, help="Longitude right.")
    parser.add_argument('--DATA_VARIABLE_NAME', default=None, required=False, help="Data variable name.")
    parser.add_argument('--TIME_VARIABLE_NAME', default=None, required=False, help="Time variable name.")
    parser.add_argument('--AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION', default=None, required=False,help="Average ATLITE capacity factors file location.")
    parser.add_argument('--PERCENT_UPPER_TIER1_CAPACITY_FACTORS', default=None, required=False,help="Upper % tier 1 for capacity factors.")
    parser.add_argument('--PERCENT_UPPER_TIER2_CAPACITY_FACTORS', default=None, required=False,help="Upper % tier 2 for capacity factors.")
    parser.add_argument('--PERCENT_UPPER_TIER3_CAPACITY_FACTORS', default=None, required=False,help="Upper % tier 3 for capacity factors.")
    parser.add_argument('--PERCENT_UPPER_TIER4_CAPACITY_FACTORS', default=None, required=False,help="Upper % tier 4 for capacity factors.")
    parser.add_argument('--PERCENT_UPPER_TIER5_CAPACITY_FACTORS', default=None, required=False,help="Upper % tier 5 for capacity factors.")
    parser.add_argument('--AVG_ATLITE_LATITUDE_VARIABLE_NAME', default=None, required=False,help="Average ATLITE latitude variable name.")
    parser.add_argument('--AVG_ATLITE_LONGITUDE_VARIABLE_NAME', default=None, required=False,help="Average ATLITE longitude variable name.")
    parser.add_argument('--OPTION_3_OUTPUT_FOLDER', default=None, required=False, help="Option 3 output folder.")
    parser.add_argument('--MAXIMUM_CAPACITY', default=None, required=False, help="Maximum capacity.")
    parser.add_argument('--BOUND_CAPACITY_FACTORS_TIME_SERIES_FILE_3', default=None, required=False,help="Output file for the capacity factors time series.")
    parser.add_argument('--SCALE_CAPACITY_FACTORS', default=None, required=False,help="Scale capacity factors with the maximum capacity.")

    # parse args
    args = parser.parse_args()

    # Check if all arguments are provided
    if all(arg is None for arg in vars(args).values()):
        raise ValueError("ERROR: All arguments are None!")

    # Check if any of the arguments are provided
    if any(arg is None for arg in vars(args).values()):
        print("Warning only some arguments provided! Code may fail.")

    return args


def load_from_env():
    # load data from .env file
    load_dotenv()

    env_vars = {
        'ATLITE_DUMMY_DATA': os.environ.get('ATLITE_DUMMY_DATA'),
        "ATLITE_CAPACITY_FACTORS_FOLDERS" : os.environ.get("ATLITE_CAPACITY_FACTORS_FOLDERS"),
        'DUMMY_START_DATE': os.environ.get('DUMMY_START_DATE'),
        'DUMMY_END_DATE': os.environ.get('DUMMY_END_DATE'),
        'DUMMY_LATITUDE_BOTTOM': os.environ.get('DUMMY_LATITUDE_BOTTOM'),
        'DUMMY_LATITUDE_TOP': os.environ.get('DUMMY_LATITUDE_TOP'),
        'DUMMY_LONGITUDE_LEFT': os.environ.get('DUMMY_LONGITUDE_LEFT'),
        'DUMMY_LONGITUDE_RIGHT': os.environ.get('DUMMY_LONGITUDE_RIGHT'),
        'DATA_VARIABLE_NAME': os.environ.get('DATA_VARIABLE_NAME'),
        'TIME_VARIABLE_NAME': os.environ.get('TIME_VARIABLE_NAME'),
        'AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION': os.environ.get('AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION'),
        'PERCENT_UPPER_TIER1_CAPACITY_FACTORS': os.environ.get('PERCENT_UPPER_TIER1_CAPACITY_FACTORS'),
        'PERCENT_UPPER_TIER2_CAPACITY_FACTORS': os.environ.get('PERCENT_UPPER_TIER2_CAPACITY_FACTORS'),
        'PERCENT_UPPER_TIER3_CAPACITY_FACTORS': os.environ.get('PERCENT_UPPER_TIER3_CAPACITY_FACTORS'),
        'PERCENT_UPPER_TIER4_CAPACITY_FACTORS': os.environ.get('PERCENT_UPPER_TIER4_CAPACITY_FACTORS'),
        'PERCENT_UPPER_TIER5_CAPACITY_FACTORS': os.environ.get('PERCENT_UPPER_TIER5_CAPACITY_FACTORS'),
        'AVG_ATLITE_LATITUDE_VARIABLE_NAME': os.environ.get('AVG_ATLITE_LATITUDE_VARIABLE_NAME'),
        'AVG_ATLITE_LONGITUDE_VARIABLE_NAME': os.environ.get('AVG_ATLITE_LONGITUDE_VARIABLE_NAME'),
        'OPTION_3_OUTPUT_FOLDER': os.environ.get('OPTION_3_OUTPUT_FOLDER'),
        'MAXIMUM_CAPACITY': os.environ.get('MAXIMUM_CAPACITY'),
        'BOUND_CAPACITY_FACTORS_TIME_SERIES_FILE_3': os.environ.get('BOUND_CAPACITY_FACTORS_TIME_SERIES_FILE_3'),
        'SCALE_CAPACITY_FACTORS': os.environ.get('SCALE_CAPACITY_FACTORS'),
    }


    # Store the names of variables that are None
    unset_variables = []

    for key, value in env_vars.items():
        if value is None:
            unset_variables.append(key)

    if unset_variables:
        print("WARNING: The following environment variables are not set in the .env file:")
        for var in unset_variables:
            print("...... -  ", var)

    return env_vars

################################################################
# main codes:

def average_capacity_factors_atlite(ATLITE_DUMMY_DATA, ATLITE_CAPACITY_FACTORS_FOLDERS, DUMMY_START_DATE, DUMMY_END_DATE, DUMMY_LATITUDE_BOTTOM, DUMMY_LATITUDE_TOP, DUMMY_LONGITUDE_LEFT, DUMMY_LONGITUDE_RIGHT, DATA_VARIABLE_NAME, TIME_VARIABLE_NAME, AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION, PERCENT_UPPER_TIER1_CAPACITY_FACTORS, PERCENT_UPPER_TIER2_CAPACITY_FACTORS, PERCENT_UPPER_TIER3_CAPACITY_FACTORS, PERCENT_UPPER_TIER4_CAPACITY_FACTORS, PERCENT_UPPER_TIER5_CAPACITY_FACTORS, AVG_ATLITE_LATITUDE_VARIABLE_NAME, AVG_ATLITE_LONGITUDE_VARIABLE_NAME, OPTION_3_OUTPUT_FOLDER, MAXIMUM_CAPACITY, BOUND_CAPACITY_FACTORS_TIME_SERIES_FILE_3, SCALE_CAPACITY_FACTORS):
    # average the capacity factors according to time:
    atlite_capacity_factors, atlite_capacity_factors_avg = support_functions.create_average_capacity_factor_file_atlite(ATLITE_DUMMY_DATA, ATLITE_CAPACITY_FACTORS_FOLDERS,DUMMY_START_DATE,DUMMY_END_DATE,DUMMY_LATITUDE_BOTTOM,DUMMY_LATITUDE_TOP,DUMMY_LONGITUDE_LEFT,DUMMY_LONGITUDE_RIGHT,MAXIMUM_CAPACITY,DATA_VARIABLE_NAME,TIME_VARIABLE_NAME,AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION)
    print("... Averaged atlite capacity factor data.")


    # Option 3: Split tiers according to percentage bounds:
    def get_tier_percentage_bound(lats,longs,atlite_data,selected_data):
        # count as the values get added on to take the average at the end
        number_columns_in_tier = 0
        # skeleton to hold the values
        cumulative_average_values = np.zeros((len(atlite_data[DATA_VARIABLE_NAME].values[:,0,0])))

        # loop through and find if nan or data
        for lat in range(len(lats)):
            for lon in range(len(longs)):
                value = selected_data.data[lat][lon]
                if np.isnan(value):
                    continue
                else:
                    # Add the new column to the skeleton column
                    cumulative_average_values += atlite_data[DATA_VARIABLE_NAME].values[:, lat, lon]
                    number_columns_in_tier += 1

        # take the average
        print("... A tier was created.")
        return cumulative_average_values/number_columns_in_tier

    # Convert the PERCENT_UPPER_TIER1_CAPACITY_FACTORS variable to a list of floats
    percent_upper_tier1_capacity_factors = list(map(float, PERCENT_UPPER_TIER1_CAPACITY_FACTORS.split(',')))
    percent_upper_tier2_capacity_factors = list(map(float, PERCENT_UPPER_TIER2_CAPACITY_FACTORS.split(',')))
    percent_upper_tier3_capacity_factors = list(map(float, PERCENT_UPPER_TIER3_CAPACITY_FACTORS.split(',')))
    percent_upper_tier4_capacity_factors = list(map(float, PERCENT_UPPER_TIER4_CAPACITY_FACTORS.split(',')))
    percent_upper_tier5_capacity_factors = list(map(float, PERCENT_UPPER_TIER5_CAPACITY_FACTORS.split(',')))

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
    bounds_tier1 = copy.deepcopy(atlite_capacity_factors_avg).stack(z=(AVG_ATLITE_LATITUDE_VARIABLE_NAME, AVG_ATLITE_LONGITUDE_VARIABLE_NAME)).quantile([lower_percentile_tier1, upper_percentile_tier1], dim='z')
    bounds_tier2 = copy.deepcopy(atlite_capacity_factors_avg).stack(z=(AVG_ATLITE_LATITUDE_VARIABLE_NAME, AVG_ATLITE_LONGITUDE_VARIABLE_NAME)).quantile([lower_percentile_tier2, upper_percentile_tier2], dim='z')
    bounds_tier3 = copy.deepcopy(atlite_capacity_factors_avg).stack(z=(AVG_ATLITE_LATITUDE_VARIABLE_NAME, AVG_ATLITE_LONGITUDE_VARIABLE_NAME)).quantile([lower_percentile_tier3, upper_percentile_tier3], dim='z')
    bounds_tier4 = copy.deepcopy(atlite_capacity_factors_avg).stack(z=(AVG_ATLITE_LATITUDE_VARIABLE_NAME, AVG_ATLITE_LONGITUDE_VARIABLE_NAME)).quantile([lower_percentile_tier4, upper_percentile_tier4], dim='z')
    bounds_tier5 = copy.deepcopy(atlite_capacity_factors_avg).stack(z=(AVG_ATLITE_LATITUDE_VARIABLE_NAME, AVG_ATLITE_LONGITUDE_VARIABLE_NAME)).quantile([lower_percentile_tier5, upper_percentile_tier5], dim='z')

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
    bound_tier1 = get_tier_percentage_bound(atlite_capacity_factors[AVG_ATLITE_LATITUDE_VARIABLE_NAME].values,atlite_capacity_factors[AVG_ATLITE_LONGITUDE_VARIABLE_NAME].values,copy.deepcopy(atlite_capacity_factors),selected_indexes_tier1)
    bound_tier2 = get_tier_percentage_bound(atlite_capacity_factors[AVG_ATLITE_LATITUDE_VARIABLE_NAME].values,atlite_capacity_factors[AVG_ATLITE_LONGITUDE_VARIABLE_NAME].values,copy.deepcopy(atlite_capacity_factors),selected_indexes_tier2)
    bound_tier3 = get_tier_percentage_bound(atlite_capacity_factors[AVG_ATLITE_LATITUDE_VARIABLE_NAME].values,atlite_capacity_factors[AVG_ATLITE_LONGITUDE_VARIABLE_NAME].values,copy.deepcopy(atlite_capacity_factors),selected_indexes_tier3)
    bound_tier4 = get_tier_percentage_bound(atlite_capacity_factors[AVG_ATLITE_LATITUDE_VARIABLE_NAME].values,atlite_capacity_factors[AVG_ATLITE_LONGITUDE_VARIABLE_NAME].values,copy.deepcopy(atlite_capacity_factors),selected_indexes_tier4)
    bound_tier5 = get_tier_percentage_bound(atlite_capacity_factors[AVG_ATLITE_LATITUDE_VARIABLE_NAME].values,atlite_capacity_factors[AVG_ATLITE_LONGITUDE_VARIABLE_NAME].values,copy.deepcopy(atlite_capacity_factors),selected_indexes_tier5)
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
    if not os.path.exists(OPTION_3_OUTPUT_FOLDER):
        os.makedirs(OPTION_3_OUTPUT_FOLDER)


    # scale capacity factors if required:
    if SCALE_CAPACITY_FACTORS.lower() == "true":
        tier_dataframe_option_3 = tier_dataframe_option_3/float(MAXIMUM_CAPACITY)  # divide by the weightings
        print("\n... Capacity factors were scaled by division of maximum capacity:",MAXIMUM_CAPACITY)


    tier_dataframe_option_3.to_csv(os.path.join(OPTION_3_OUTPUT_FOLDER,BOUND_CAPACITY_FACTORS_TIME_SERIES_FILE_3),index=False)


    print("\nOption_3 completed successfully!")

if __name__ == '__main__':

    print("#########")
    print("Option 3")
    print("#########")

    # check args or load env file and run codes
    try:
        print("TRYING TO USE ARGUMENTS")
        args = parse_arguments()
        print("ARGUMENTS FOUND. USING ARGUMENTS")

        # RUN CODES
        average_capacity_factors_atlite(**vars(args))
    except Exception as e:
        print("ARGUMENTS NOT FOUND: ", e)
        try:
            print("TRYING TO LOAD ENV FILE VARIABLES")
            # Load variables from the .env file
            args = load_from_env()
            print("ENV FILE FOUND. USING ENV FILE")

            # RUN CODES
            average_capacity_factors_atlite(**args)

        except Exception as e:
            print("ENV FILE NOT FOUND: ", e)
            print("ERROR ... USER ARGS AND ENV FILE NOT FOUND, ABORTING!")
            raise ValueError("COULD NOT FIND ARGS OR LOAD ENV FILE. USER ARGS OR ENV FILE MISSING.")

    # args example use:
    # python Option_3_bound_percentage_atlite.py  --ATLITE_DUMMY_DATA=True  --DUMMY_START_DATE='2023-01-01'  --DUMMY_END_DATE='2024-01-01'  --DUMMY_LATITUDE_BOTTOM=-32.0  --DUMMY_LATITUDE_TOP=-30.0  --DUMMY_LONGITUDE_LEFT=26.0  --DUMMY_LONGITUDE_RIGHT=28.0  --DATA_VARIABLE_NAME=capacity_factors  --TIME_VARIABLE_NAME=time  --AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION="assets/avg_atlite_capacity_factors.nc"  --PERCENT_UPPER_TIER1_CAPACITY_FACTORS=0,10  --PERCENT_UPPER_TIER2_CAPACITY_FACTORS=10,20  --PERCENT_UPPER_TIER3_CAPACITY_FACTORS=0,40  --PERCENT_UPPER_TIER4_CAPACITY_FACTORS=60,100  --PERCENT_UPPER_TIER5_CAPACITY_FACTORS=40,60  --AVG_ATLITE_LATITUDE_VARIABLE_NAME=latitude  --AVG_ATLITE_LONGITUDE_VARIABLE_NAME=longitude  --OPTION_3_OUTPUT_FOLDER="assets/option_3_output"  --MAXIMUM_CAPACITY=50  --BOUND_CAPACITY_FACTORS_TIME_SERIES_FILE_3="option_3_top_percentage_capacity_factor_time_series.csv"  --SCALE_CAPACITY_FACTORS=True
