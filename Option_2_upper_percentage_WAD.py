"""
Purpose: Finds the upper percentage capacity factors for the WIND ATLAS data. Then pulls the closest location timeseries data from the Atlite data and averages then to form a tier.

Author: Kirodh Boodhraj
"""
import numpy as np
import os
from dotenv import load_dotenv
import copy
import pandas as pd
import warnings
import argparse

import Option_Support_Functions as support_functions



################################
# system args section
################################
# used for running the codes
def parse_arguments():
    parser = argparse.ArgumentParser(description="(Option 2) Script to calculate average capacity factors.")
    parser.add_argument('--ATLITE_DUMMY_DATA', default=None, required=False,help="Boolean to use the dummy Atlite data (True) or not.")
    parser.add_argument('--ATLITE_CAPACITY_FACTORS_FOLDERS', default=None, required=False,help="Folders continaing hourly Atlite data files needing stitching.")
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
    parser.add_argument('--REDUCED_WAD', default=None, required=False, help="Whether to use reduced WAD data.")
    parser.add_argument('--WIND_ATLAS_RESOLUTION_REDUCTION', default=None, required=False,help="WIND ATLAS resolution reduction.")
    parser.add_argument('--WIND_ATLAS_CAPACITY_FACTORS_HEATMAP_FILE_LOCATION', default=None, required=False,help="WIND ATLAS capacity factors heatmap file location.")
    parser.add_argument('--WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME', default=None, required=False,help="WIND ATLAS heatmap latitude variable name.")
    parser.add_argument('--WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME', default=None, required=False,help="WIND ATLAS heatmap longitude variable name.")
    parser.add_argument('--WIND_ATLAS_HEATMAP_DATA_VARIABLE_NAME', default=None, required=False,help="WIND ATLAS heatmap data variable name.")
    parser.add_argument('--PERCENT_UPPER_CAPACITY_FACTORS_2', default=None, required=False,help="Percentage upper capacity factors 2.")
    parser.add_argument('--OPTION_2_OUTPUT_FOLDER', default=None, required=False, help="Option 2 output folder.")
    parser.add_argument('--SCALE_CAPACITY_FACTORS', default=None, required=False, help="Scale capacity factors.")
    parser.add_argument('--PERCENT_UPPER_CAPACITY_FACTORS_TIME_SERIES_FILE_2', default=None, required=False, help="Output file for the capacity factors time series.")
    parser.add_argument('--PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE_WAD_2', default=None, required=False, help="Output file for the capacity factors Wind Atlas Data.")
    parser.add_argument('--PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE_ATLITE_2', default=None, required=False, help="Output file for the capacity factors Atlite data.")

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
    # Load data from .env file
    load_dotenv()
    env_vars = {
        "ATLITE_DUMMY_DATA": os.environ.get("ATLITE_DUMMY_DATA"),
        "ATLITE_CAPACITY_FACTORS_FOLDERS" : os.environ.get("ATLITE_CAPACITY_FACTORS_FOLDERS"),
        "DUMMY_START_DATE": os.environ.get("DUMMY_START_DATE"),
        "DUMMY_END_DATE": os.environ.get("DUMMY_END_DATE"),
        "DUMMY_LATITUDE_BOTTOM": os.environ.get("DUMMY_LATITUDE_BOTTOM"),
        "DUMMY_LATITUDE_TOP": os.environ.get("DUMMY_LATITUDE_TOP"),
        "DUMMY_LONGITUDE_LEFT": os.environ.get("DUMMY_LONGITUDE_LEFT"),
        "DUMMY_LONGITUDE_RIGHT": os.environ.get("DUMMY_LONGITUDE_RIGHT"),
        "MAXIMUM_CAPACITY": os.environ.get("MAXIMUM_CAPACITY"),
        "DATA_VARIABLE_NAME": os.environ.get("DATA_VARIABLE_NAME"),
        "TIME_VARIABLE_NAME": os.environ.get("TIME_VARIABLE_NAME"),
        "AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION": os.environ.get("AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION"),
        "AVG_ATLITE_LATITUDE_VARIABLE_NAME": os.environ.get("AVG_ATLITE_LATITUDE_VARIABLE_NAME"),
        "AVG_ATLITE_LONGITUDE_VARIABLE_NAME": os.environ.get("AVG_ATLITE_LONGITUDE_VARIABLE_NAME"),
        "REDUCED_WAD": os.environ.get("REDUCED_WAD"),
        "WIND_ATLAS_RESOLUTION_REDUCTION": os.environ.get("WIND_ATLAS_RESOLUTION_REDUCTION"),
        "WIND_ATLAS_CAPACITY_FACTORS_HEATMAP_FILE_LOCATION": os.environ.get("WIND_ATLAS_CAPACITY_FACTORS_HEATMAP_FILE_LOCATION"),
        "WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME": os.environ.get("WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME"),
        "WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME": os.environ.get("WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME"),
        "WIND_ATLAS_HEATMAP_DATA_VARIABLE_NAME": os.environ.get("WIND_ATLAS_HEATMAP_DATA_VARIABLE_NAME"),
        "PERCENT_UPPER_CAPACITY_FACTORS_2": os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS_2"),
        "OPTION_2_OUTPUT_FOLDER": os.environ.get("OPTION_2_OUTPUT_FOLDER"),
        "SCALE_CAPACITY_FACTORS": os.environ.get("SCALE_CAPACITY_FACTORS"),
        "PERCENT_UPPER_CAPACITY_FACTORS_TIME_SERIES_FILE_2": os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS_TIME_SERIES_FILE_2"),
        "PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE_WAD_2": os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE_WAD_2"),
        "PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE_ATLITE_2": os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE_ATLITE_2"),
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

def average_capacity_factors_WAD(ATLITE_DUMMY_DATA, ATLITE_CAPACITY_FACTORS_FOLDERS, DUMMY_START_DATE, DUMMY_END_DATE, DUMMY_LATITUDE_BOTTOM, DUMMY_LATITUDE_TOP, DUMMY_LONGITUDE_LEFT, DUMMY_LONGITUDE_RIGHT, MAXIMUM_CAPACITY, DATA_VARIABLE_NAME, TIME_VARIABLE_NAME, AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION, AVG_ATLITE_LATITUDE_VARIABLE_NAME, AVG_ATLITE_LONGITUDE_VARIABLE_NAME, REDUCED_WAD, WIND_ATLAS_RESOLUTION_REDUCTION, WIND_ATLAS_CAPACITY_FACTORS_HEATMAP_FILE_LOCATION, WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME, WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME, WIND_ATLAS_HEATMAP_DATA_VARIABLE_NAME, PERCENT_UPPER_CAPACITY_FACTORS_2, OPTION_2_OUTPUT_FOLDER, SCALE_CAPACITY_FACTORS, PERCENT_UPPER_CAPACITY_FACTORS_TIME_SERIES_FILE_2, PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE_WAD_2, PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE_ATLITE_2):
    # Code block where you want to suppress warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        # average the capacity factors according to time:
        atlite_capacity_factors, atlite_capacity_factors_avg = support_functions.create_average_capacity_factor_file_atlite(ATLITE_DUMMY_DATA, ATLITE_CAPACITY_FACTORS_FOLDERS,DUMMY_START_DATE,DUMMY_END_DATE,DUMMY_LATITUDE_BOTTOM,DUMMY_LATITUDE_TOP,DUMMY_LONGITUDE_LEFT,DUMMY_LONGITUDE_RIGHT,MAXIMUM_CAPACITY,DATA_VARIABLE_NAME,TIME_VARIABLE_NAME,AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION)
        atlite_lats = atlite_capacity_factors[AVG_ATLITE_LATITUDE_VARIABLE_NAME]
        atlite_lons = atlite_capacity_factors[AVG_ATLITE_LONGITUDE_VARIABLE_NAME]
        print("... Read averaged atlite capacity factor data.")

        if REDUCED_WAD.lower() == "true":
            # open the WAD data
            latitude_wad,longitude_wad,all_data_wad = support_functions.read_wind_atlas_data_reduced(WIND_ATLAS_RESOLUTION_REDUCTION,WIND_ATLAS_CAPACITY_FACTORS_HEATMAP_FILE_LOCATION,WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME,WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME,WIND_ATLAS_HEATMAP_DATA_VARIABLE_NAME)
        else:
            # open the WAD data
            latitude_wad, longitude_wad, all_data_wad = support_functions.read_wind_atlas_data_full(WIND_ATLAS_CAPACITY_FACTORS_HEATMAP_FILE_LOCATION,WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME,WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME,WIND_ATLAS_HEATMAP_DATA_VARIABLE_NAME)

        # Save top % capacity factors and generate a time series from that
        print("... Generating time series from top "+PERCENT_UPPER_CAPACITY_FACTORS_2+" capacity factors")
        try:
            check_percentage = float(PERCENT_UPPER_CAPACITY_FACTORS_2)
            if check_percentage < 0:
                ValueError("The percentage is less than 0. Only 0-100 allowed.")
            if check_percentage > 100:
                ValueError("The percentage is larger than 100. Only 0-100 allowed.")
        except Exception as e:
            ValueError("The percentage is not a number. Only 0-100 allowed.")
        # Find the top % values from the temporal average
        top_percentage = copy.deepcopy(all_data_wad).stack(z=(WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME, WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME)).quantile(1.0 - float(PERCENT_UPPER_CAPACITY_FACTORS_2)/100)
        # print(top_percentage)

        # Use boolean indexing to select the desired indexes
        selected_indexes = all_data_wad.where(all_data_wad>top_percentage)#, drop=True)
        # print(selected_indexes)

        # get lats/lons
        latitudes = selected_indexes[WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME].values
        longitudes = selected_indexes[WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME].values

        non_nan_indices = np.argwhere(~np.isnan(selected_indexes.data))
        # print(len(non_nan_indices))

        # empty shell to store the lats/lons and the data, then average them later
        # check if output directories are created
        if not os.path.exists(OPTION_2_OUTPUT_FOLDER):
            os.makedirs(OPTION_2_OUTPUT_FOLDER)

        lat_lon_df_atlite = pd.DataFrame(columns=['latitude', 'longitude','average_capacity_factor'])
        lat_lon_df_wad = pd.DataFrame(columns=['latitude', 'longitude','average_capacity_factor'])
        tiers_raw_df = pd.DataFrame()

        for index_number,index_pair in enumerate(non_nan_indices): # index pair has lat then lon
            print("Busy with index: ",index_number+1," out of: ",len(non_nan_indices))

            # get value
            value = selected_indexes.data[index_pair[0]][index_pair[1]]

            # add data to the data frame
            # lat/lon wad
            lat_lon_df_wad.loc[len(lat_lon_df_wad)] = [latitudes[index_pair[0]],longitudes[index_pair[1]],value]

            # get lat lon corresponding to atlite data:
            closest_lat_index = np.argmin(np.abs(latitudes[index_pair[0]]-atlite_lats.values))
            closest_lon_index = np.argmin(np.abs(longitudes[index_pair[1]]-atlite_lons.values))

            # lat/lon atlite
            lat_lon_df_atlite.loc[len(lat_lon_df_atlite)] = [atlite_lats.values[closest_lat_index],atlite_lons.values[closest_lon_index],atlite_capacity_factors_avg.data[closest_lat_index,closest_lon_index]]

            # timeseries
            # Determine the next number for the new column name
            next_column_number = len(tiers_raw_df.columns) + 1
            # Create a new column name
            new_column_name = f'tier_{next_column_number}'
            # Add the new column to the DataFrame
            tiers_raw_df[new_column_name] = atlite_capacity_factors[DATA_VARIABLE_NAME].values[:,closest_lat_index,closest_lon_index]

        # # get the final tier and save it
        tiers_raw_df['average_tier_final'] = tiers_raw_df.mean(axis=1)

        # scale capacity factors if required:
        if SCALE_CAPACITY_FACTORS.lower() == "true":
            tiers_raw_df = tiers_raw_df / float(MAXIMUM_CAPACITY)  # divide by the weightings
            print("\n... Capacity factors were scaled by division of maximum capacity:",MAXIMUM_CAPACITY)

        # save to csv files
        tiers_raw_df.to_csv(os.path.join(OPTION_2_OUTPUT_FOLDER,PERCENT_UPPER_CAPACITY_FACTORS_TIME_SERIES_FILE_2))
        lat_lon_df_wad.to_csv(os.path.join(OPTION_2_OUTPUT_FOLDER,PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE_WAD_2))
        lat_lon_df_atlite.to_csv(os.path.join(OPTION_2_OUTPUT_FOLDER,PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE_ATLITE_2))

        print("\n... Tier files for top "+PERCENT_UPPER_CAPACITY_FACTORS_2+" capacity factors created:")
        print("...... ATLITE Location file located in: "+PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE_ATLITE_2)
        print("...... WIND ATLAS DATA Location file located in: "+PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE_WAD_2)
        print("...... Tier file located in: "+PERCENT_UPPER_CAPACITY_FACTORS_TIME_SERIES_FILE_2)
        print("... Note that averaged tier is in average_tier_final column.")

        print("\nOption_2 completed successfully!")


if __name__ == '__main__':
    print("#########")
    print("Option 2")
    print("#########")

    # check args or load env file and run codes
    try:
        print("TRYING TO USE ARGUMENTS")
        args = parse_arguments()
        print("ARGUMENTS FOUND. USING ARGUMENTS")

        # RUN CODES
        average_capacity_factors_WAD(**vars(args))
    except Exception as e:
        print("ARGUMENTS NOT FOUND: ",e)
        try:
            print("TRYING TO LOAD ENV FILE VARIABLES")
            # Load variables from the .env file
            args = load_from_env()
            print("ENV FILE FOUND. USING ENV FILE")

            # RUN CODES
            average_capacity_factors_WAD(**args)

        except Exception as e:
            print("ENV FILE NOT FOUND: ",e)
            print("ERROR ... USER ARGS AND ENV FILE NOT FOUND, ABORTING!")
            raise ValueError("COULD NOT FIND ARGS OR LOAD ENV FILE. USER ARGS OR ENV FILE MISSING.")

    # example use:
    # python Option_2_upper_percentage_WAD.py --ATLITE_DUMMY_DATA True --DUMMY_START_DATE  '2023-01-01' --DUMMY_END_DATE  '2024-01-01' --DUMMY_LATITUDE_BOTTOM  -32.0 --DUMMY_LATITUDE_TOP  -30.0 --DUMMY_LONGITUDE_LEFT  26.0 --DUMMY_LONGITUDE_RIGHT  28.0 --MAXIMUM_CAPACITY  50 --DATA_VARIABLE_NAME  capacity_factors --TIME_VARIABLE_NAME  time --AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION  "assets/avg_atlite_capacity_factors.nc" --AVG_ATLITE_LATITUDE_VARIABLE_NAME  latitude --AVG_ATLITE_LONGITUDE_VARIABLE_NAME  longitude --REDUCED_WAD  True --WIND_ATLAS_RESOLUTION_REDUCTION  15 --WIND_ATLAS_CAPACITY_FACTORS_HEATMAP_FILE_LOCATION  "assets/wind_atlas_capacity_factors.nc" --WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME  lat --WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME  lon --WIND_ATLAS_HEATMAP_DATA_VARIABLE_NAME  Band1 --PERCENT_UPPER_CAPACITY_FACTORS_2  10 --OPTION_2_OUTPUT_FOLDER  "assets/option_2_output" --SCALE_CAPACITY_FACTORS  True --PERCENT_UPPER_CAPACITY_FACTORS_TIME_SERIES_FILE_2  "option_2_top_percentage_capacity_factor_time_series.csv" --PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE_WAD_2  "option_2_top_percentage_locations_wad.csv" --PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE_ATLITE_2  "option_2_top_percentage_locations_atlite.csv"