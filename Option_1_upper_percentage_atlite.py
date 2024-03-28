"""
Purpose: Returns the upper percentage averaged capacity factors for the ATLITE data.

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
    parser = argparse.ArgumentParser(description="(Option 1) Script to calculate average capacity factors.")
    parser.add_argument('--ATLITE_DUMMY_DATA', default=None, required=False, help="Boolean to use the dummy Atlite data (True) or not.")
    parser.add_argument('--DUMMY_START_DATE', default=None, required=False, help="Start date.")
    parser.add_argument('--DUMMY_END_DATE', default=None, required=False, help="End date.")
    parser.add_argument('--DUMMY_LATITUDE_BOTTOM', default=None, required=False, help="Latitude bottom.")
    parser.add_argument('--DUMMY_LATITUDE_TOP', default=None, required=False, help="Latitude top.")
    parser.add_argument('--DUMMY_LONGITUDE_LEFT', default=None, required=False, help="Longitude left.")
    parser.add_argument('--DUMMY_LONGITUDE_RIGHT', default=None, required=False, help="Longitude right.")
    parser.add_argument('--MAXIMUM_CAPACITY', default=None, required=False, help="Maximum capacity.")
    parser.add_argument('--DATA_VARIABLE_NAME', default=None, required=False, help="Data variable name.")
    parser.add_argument('--TIME_VARIABLE_NAME', default=None, required=False, help="Time variable name.")
    parser.add_argument('--AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION', default=None, required=False,help="Average ATLITE capacity factors file location.")
    parser.add_argument('--AVG_ATLITE_LATITUDE_VARIABLE_NAME', default=None, required=False,help="Average ATLITE latitude variable name.")
    parser.add_argument('--AVG_ATLITE_LONGITUDE_VARIABLE_NAME', default=None, required=False,help="Average ATLITE longitude variable name.")
    parser.add_argument('--PERCENT_UPPER_CAPACITY_FACTORS_1', default=None, required=False,help="Percentage upper capacity factors 1.")
    parser.add_argument('--OPTION_1_OUTPUT_FOLDER', default=None, required=False, help="Option 1 output folder.")
    parser.add_argument('--PERCENT_UPPER_CAPACITY_FACTORS_TIME_SERIES_FILE_1', default=None, required=False,help="Percentage upper capacity factors time series file 1.")
    parser.add_argument('--PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE_1', default=None, required=False,help="Percentage upper capacity factors location file 1.")
    parser.add_argument('--SCALE_CAPACITY_FACTORS', default=None, required=False, help="Scale capacity factors.")

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
    env_vars =  {
        "ATLITE_DUMMY_DATA" : os.environ.get("ATLITE_DUMMY_DATA"),
        "DUMMY_START_DATE" : os.environ.get("DUMMY_START_DATE"),
        "DUMMY_END_DATE" : os.environ.get("DUMMY_END_DATE"),
        "DUMMY_LATITUDE_BOTTOM" : os.environ.get("DUMMY_LATITUDE_BOTTOM"),
        "DUMMY_LATITUDE_TOP" : os.environ.get("DUMMY_LATITUDE_TOP"),
        "DUMMY_LONGITUDE_LEFT" : os.environ.get("DUMMY_LONGITUDE_LEFT"),
        "DUMMY_LONGITUDE_RIGHT" : os.environ.get("DUMMY_LONGITUDE_RIGHT"),
        "MAXIMUM_CAPACITY" : os.environ.get("MAXIMUM_CAPACITY"),
        "DATA_VARIABLE_NAME" : os.environ.get("DATA_VARIABLE_NAME"),
        "TIME_VARIABLE_NAME" : os.environ.get("TIME_VARIABLE_NAME"),
        "AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION" : os.environ.get("AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION"),
        "AVG_ATLITE_LATITUDE_VARIABLE_NAME" : os.environ.get("AVG_ATLITE_LATITUDE_VARIABLE_NAME"),
        "AVG_ATLITE_LONGITUDE_VARIABLE_NAME" : os.environ.get("AVG_ATLITE_LONGITUDE_VARIABLE_NAME"),
        "PERCENT_UPPER_CAPACITY_FACTORS_1" : os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS_1"),
        "OPTION_1_OUTPUT_FOLDER" : os.environ.get("OPTION_1_OUTPUT_FOLDER"),
        "PERCENT_UPPER_CAPACITY_FACTORS_TIME_SERIES_FILE_1" : os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS_TIME_SERIES_FILE_1"),
        "PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE_1" : os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE_1"),
        "SCALE_CAPACITY_FACTORS" : os.environ.get("SCALE_CAPACITY_FACTORS"),
    }
    # if None in env_vars.values():
    #     # raise ValueError("One or more environment variables are not set in the .env file.")
    #     print("WARNING: One or more environment variables are not set in the .env file!")

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

def average_capacity_factors_atlite(ATLITE_DUMMY_DATA, DUMMY_START_DATE, DUMMY_END_DATE, DUMMY_LATITUDE_BOTTOM, DUMMY_LATITUDE_TOP, DUMMY_LONGITUDE_LEFT, DUMMY_LONGITUDE_RIGHT, MAXIMUM_CAPACITY, DATA_VARIABLE_NAME, TIME_VARIABLE_NAME, AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION, AVG_ATLITE_LATITUDE_VARIABLE_NAME, AVG_ATLITE_LONGITUDE_VARIABLE_NAME, PERCENT_UPPER_CAPACITY_FACTORS_1, OPTION_1_OUTPUT_FOLDER, PERCENT_UPPER_CAPACITY_FACTORS_TIME_SERIES_FILE_1, PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE_1, SCALE_CAPACITY_FACTORS):
    # average the capacity factors according to time:
    atlite_capacity_factors, atlite_capacity_factors_avg = support_functions.create_average_capacity_factor_file_atlite(ATLITE_DUMMY_DATA,DUMMY_START_DATE,DUMMY_END_DATE,DUMMY_LATITUDE_BOTTOM,DUMMY_LATITUDE_TOP,DUMMY_LONGITUDE_LEFT,DUMMY_LONGITUDE_RIGHT,MAXIMUM_CAPACITY,DATA_VARIABLE_NAME,TIME_VARIABLE_NAME,AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION)
    print("... Read averaged atlite capacity factor data.")

    # Save top % capacity factors and generate a time series from that
    print("... Generating time series from top "+PERCENT_UPPER_CAPACITY_FACTORS_1+" capacity factors")
    try:
        check_percentage = float(PERCENT_UPPER_CAPACITY_FACTORS_1)
        if check_percentage < 0:
            ValueError("The percentage is less than 0. Only 0-100 allowed.")
        if check_percentage > 100:
            ValueError("The percentage is larger than 100. Only 0-100 allowed.")
    except Exception as e:
        ValueError("The percentage is not a number. Only 0-100 allowed.")
    # Find the top % values from the temporal average
    top_percentage = copy.deepcopy(atlite_capacity_factors_avg).stack(z=(AVG_ATLITE_LATITUDE_VARIABLE_NAME, AVG_ATLITE_LONGITUDE_VARIABLE_NAME)).quantile(1.0 - float(PERCENT_UPPER_CAPACITY_FACTORS_1)/100)


    # Use boolean indexing to select the desired indexes
    selected_indexes = atlite_capacity_factors_avg.where(atlite_capacity_factors_avg>top_percentage)#, drop=True)

    # get lats/lons
    latitudes = selected_indexes[AVG_ATLITE_LATITUDE_VARIABLE_NAME].values
    longitudes = selected_indexes[AVG_ATLITE_LONGITUDE_VARIABLE_NAME].values

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
                new_column_name = f'tier_{next_column_number}'
                # Add the new column to the DataFrame
                tiers_raw_df[new_column_name] = atlite_capacity_factors[DATA_VARIABLE_NAME].values[:,lat,lon]
                # print(value)

    # get the final tier and save it
    tiers_raw_df['average_tier_final'] = tiers_raw_df.mean(axis=1)

    # check if output directories are created
    if not os.path.exists(OPTION_1_OUTPUT_FOLDER):
        os.makedirs(OPTION_1_OUTPUT_FOLDER)

    # scale capacity factors if required:
    if SCALE_CAPACITY_FACTORS.lower() == "true":
        tiers_raw_df = tiers_raw_df/float(MAXIMUM_CAPACITY)  # divide by the weightings
        print("\n... Capacity factors were scaled by division of maximum capacity:",MAXIMUM_CAPACITY)

    tiers_raw_df.to_csv(os.path.join(OPTION_1_OUTPUT_FOLDER,PERCENT_UPPER_CAPACITY_FACTORS_TIME_SERIES_FILE_1))
    lat_lon_df.to_csv(os.path.join(OPTION_1_OUTPUT_FOLDER,PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE_1))

    print("\n... Tier files for top "+PERCENT_UPPER_CAPACITY_FACTORS_1+" capacity factors created:")
    print("...... Location file located in: "+PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE_1)
    print("...... Tier file located in: "+PERCENT_UPPER_CAPACITY_FACTORS_TIME_SERIES_FILE_1)
    print("... Note that averaged tier is in average_tier_final column.")

    print("\nOption_1 completed successfully!")


if __name__ == '__main__':
    # check args or load env file and run codes
    try:
        print("TRYING TO USE ARGUMENTS")
        args = parse_arguments()
        print("ARGUMENTS FOUND. USING ARGUMENTS")

        # RUN CODES
        average_capacity_factors_atlite(**vars(args))
    except Exception as e:
        print("ARGUMENTS NOT FOUND: ",e)
        try:
            print("TRYING TO LOAD ENV FILE VARIABLES")
            # Load variables from the .env file
            args = load_from_env()
            print("ENV FILE FOUND. USING ENV FILE")

            # RUN CODES
            average_capacity_factors_atlite(**args)

        except Exception as e:
            print("ENV FILE NOT FOUND: ",e)
            print("ERROR ... USER ARGS AND ENV FILE NOT FOUND, ABORTING!")
            raise ValueError("COULD NOT FIND ARGS OR LOAD ENV FILE. USER ARGS OR ENV FILE MISSING.")


    # args example use:
    # python Option_1_upper_percentage_atlite.py --ATLITE_DUMMY_DATA True  --DUMMY_START_DATE  '2023-01-01' --DUMMY_END_DATE '2024-01-01'  --DUMMY_LATITUDE_BOTTOM  -32 --DUMMY_LATITUDE_TOP -30  --DUMMY_LONGITUDE_LEFT 26  --DUMMY_LONGITUDE_RIGHT 28   --MAXIMUM_CAPACITY  50  --DATA_VARIABLE_NAME capacity_factors  --TIME_VARIABLE_NAME  time  --AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION "assets/avg_atlite_capacity_factors.nc" --AVG_ATLITE_LATITUDE_VARIABLE_NAME latitude --AVG_ATLITE_LONGITUDE_VARIABLE_NAME longitude --PERCENT_UPPER_CAPACITY_FACTORS_1 10  --OPTION_1_OUTPUT_FOLDER  "assets/option_1_output"  --PERCENT_UPPER_CAPACITY_FACTORS_TIME_SERIES_FILE_1  "option_1_top_percentage_capacity_factor_time_series.csv"  --PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE_1  "option_1_top_percentage_locations.csv"  --SCALE_CAPACITY_FACTORS True
