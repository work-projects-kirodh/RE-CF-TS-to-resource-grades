"""
Purpose: Finds the bounded percentage capacity factors for the WIND ATLAS data. Then pulls the closest location timeseries data from the Atlite data and averages then to form a tier fromeach bound.

Author: Kirodh Boodhraj
"""
import numpy as np
import os
from dotenv import load_dotenv
import copy
import pandas as pd
# import warnings
import argparse

import Option_Support_Functions as support_functions


################################
# system args section
################################
# used for running the codes
def parse_arguments():
    parser = argparse.ArgumentParser(description="(Option 4) Script to calculate average capacity factors.")
    parser.add_argument('--ATLITE_DUMMY_DATA', default=None, required=False,help="Boolean to use the dummy Atlite data (True) or not.")
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
    parser.add_argument('--PERCENT_UPPER_TIER1_CAPACITY_FACTORS', default=None, required=False,help="Percentage upper capacity factors for tier 1.")
    parser.add_argument('--PERCENT_UPPER_TIER2_CAPACITY_FACTORS', default=None, required=False,help="Percentage upper capacity factors for tier 2.")
    parser.add_argument('--PERCENT_UPPER_TIER3_CAPACITY_FACTORS', default=None, required=False,help="Percentage upper capacity factors for tier 3.")
    parser.add_argument('--PERCENT_UPPER_TIER4_CAPACITY_FACTORS', default=None, required=False,help="Percentage upper capacity factors for tier 4.")
    parser.add_argument('--PERCENT_UPPER_TIER5_CAPACITY_FACTORS', default=None, required=False,help="Percentage upper capacity factors for tier 5.")
    parser.add_argument('--AVG_ATLITE_DATA_VARIABLE_NAME', default=None, required=False,help="Average ATLITE data variable name.")
    parser.add_argument('--OPTION_4_OUTPUT_FOLDER', default=None, required=False, help="Option 4 output folder.")
    parser.add_argument('--SCALE_CAPACITY_FACTORS', default=None, required=False, help="Scale capacity factors.")
    parser.add_argument('--BOUND_CAPACITY_FACTORS_TIME_SERIES_FILE_4', default=None, required=False,help="Output file for the bounded capacity factors time series.")

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
        'DUMMY_START_DATE': os.environ.get('DUMMY_START_DATE'),
        'DUMMY_END_DATE': os.environ.get('DUMMY_END_DATE'),
        'DUMMY_LATITUDE_BOTTOM': os.environ.get('DUMMY_LATITUDE_BOTTOM'),
        'DUMMY_LATITUDE_TOP': os.environ.get('DUMMY_LATITUDE_TOP'),
        'DUMMY_LONGITUDE_LEFT': os.environ.get('DUMMY_LONGITUDE_LEFT'),
        'DUMMY_LONGITUDE_RIGHT': os.environ.get('DUMMY_LONGITUDE_RIGHT'),
        'MAXIMUM_CAPACITY': os.environ.get('MAXIMUM_CAPACITY'),
        'DATA_VARIABLE_NAME': os.environ.get('DATA_VARIABLE_NAME'),
        'TIME_VARIABLE_NAME': os.environ.get('TIME_VARIABLE_NAME'),
        'AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION': os.environ.get('AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION'),
        'AVG_ATLITE_LATITUDE_VARIABLE_NAME': os.environ.get('AVG_ATLITE_LATITUDE_VARIABLE_NAME'),
        'AVG_ATLITE_LONGITUDE_VARIABLE_NAME': os.environ.get('AVG_ATLITE_LONGITUDE_VARIABLE_NAME'),
        'REDUCED_WAD': os.environ.get('REDUCED_WAD'),
        'WIND_ATLAS_RESOLUTION_REDUCTION': os.environ.get('WIND_ATLAS_RESOLUTION_REDUCTION'),
        'WIND_ATLAS_CAPACITY_FACTORS_HEATMAP_FILE_LOCATION': os.environ.get('WIND_ATLAS_CAPACITY_FACTORS_HEATMAP_FILE_LOCATION'),
        'WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME': os.environ.get('WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME'),
        'WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME': os.environ.get('WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME'),
        'WIND_ATLAS_HEATMAP_DATA_VARIABLE_NAME': os.environ.get('WIND_ATLAS_HEATMAP_DATA_VARIABLE_NAME'),
        'PERCENT_UPPER_TIER1_CAPACITY_FACTORS': os.environ.get('PERCENT_UPPER_TIER1_CAPACITY_FACTORS'),
        'PERCENT_UPPER_TIER2_CAPACITY_FACTORS': os.environ.get('PERCENT_UPPER_TIER2_CAPACITY_FACTORS'),
        'PERCENT_UPPER_TIER3_CAPACITY_FACTORS': os.environ.get('PERCENT_UPPER_TIER3_CAPACITY_FACTORS'),
        'PERCENT_UPPER_TIER4_CAPACITY_FACTORS': os.environ.get('PERCENT_UPPER_TIER4_CAPACITY_FACTORS'),
        'PERCENT_UPPER_TIER5_CAPACITY_FACTORS': os.environ.get('PERCENT_UPPER_TIER5_CAPACITY_FACTORS'),
        'AVG_ATLITE_DATA_VARIABLE_NAME': os.environ.get('AVG_ATLITE_DATA_VARIABLE_NAME'),
        'OPTION_4_OUTPUT_FOLDER': os.environ.get('OPTION_4_OUTPUT_FOLDER'),
        'SCALE_CAPACITY_FACTORS': os.environ.get('SCALE_CAPACITY_FACTORS'),
        'BOUND_CAPACITY_FACTORS_TIME_SERIES_FILE_4': os.environ.get('BOUND_CAPACITY_FACTORS_TIME_SERIES_FILE_4')
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

def average_bounded_capacity_factors_WAD(ATLITE_DUMMY_DATA, DUMMY_START_DATE, DUMMY_END_DATE, DUMMY_LATITUDE_BOTTOM, DUMMY_LATITUDE_TOP, DUMMY_LONGITUDE_LEFT, DUMMY_LONGITUDE_RIGHT, MAXIMUM_CAPACITY, DATA_VARIABLE_NAME, TIME_VARIABLE_NAME, AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION, AVG_ATLITE_LATITUDE_VARIABLE_NAME, AVG_ATLITE_LONGITUDE_VARIABLE_NAME, REDUCED_WAD, WIND_ATLAS_RESOLUTION_REDUCTION, WIND_ATLAS_CAPACITY_FACTORS_HEATMAP_FILE_LOCATION, WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME, WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME, WIND_ATLAS_HEATMAP_DATA_VARIABLE_NAME, PERCENT_UPPER_TIER1_CAPACITY_FACTORS, PERCENT_UPPER_TIER2_CAPACITY_FACTORS, PERCENT_UPPER_TIER3_CAPACITY_FACTORS, PERCENT_UPPER_TIER4_CAPACITY_FACTORS, PERCENT_UPPER_TIER5_CAPACITY_FACTORS, AVG_ATLITE_DATA_VARIABLE_NAME, OPTION_4_OUTPUT_FOLDER, SCALE_CAPACITY_FACTORS, BOUND_CAPACITY_FACTORS_TIME_SERIES_FILE_4):
    # # Code block where you want to suppress warnings
    # with warnings.catch_warnings():
    #     warnings.simplefilter("ignore")

    # average the capacity factors according to time:
    atlite_capacity_factors, atlite_capacity_factors_avg = support_functions.create_average_capacity_factor_file_atlite(ATLITE_DUMMY_DATA,DUMMY_START_DATE,DUMMY_END_DATE,DUMMY_LATITUDE_BOTTOM,DUMMY_LATITUDE_TOP,DUMMY_LONGITUDE_LEFT,DUMMY_LONGITUDE_RIGHT,MAXIMUM_CAPACITY,DATA_VARIABLE_NAME,TIME_VARIABLE_NAME,AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION)
    atlite_lats = atlite_capacity_factors[AVG_ATLITE_LATITUDE_VARIABLE_NAME]
    atlite_lons = atlite_capacity_factors[AVG_ATLITE_LONGITUDE_VARIABLE_NAME]
    print("... Read averaged atlite capacity factor data.")

    if REDUCED_WAD.lower() == "true":
        # open the WAD data
        latitude_wad,longitude_wad,all_data_wad = support_functions.read_wind_atlas_data_reduced(WIND_ATLAS_RESOLUTION_REDUCTION,WIND_ATLAS_CAPACITY_FACTORS_HEATMAP_FILE_LOCATION,WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME,WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME,WIND_ATLAS_HEATMAP_DATA_VARIABLE_NAME)
    else:
        # open the WAD data
        latitude_wad, longitude_wad, all_data_wad = support_functions.read_wind_atlas_data_full(WIND_ATLAS_CAPACITY_FACTORS_HEATMAP_FILE_LOCATION,WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME,WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME,WIND_ATLAS_HEATMAP_DATA_VARIABLE_NAME)


    # Split tiers according to percentage bounds:
    def get_tier_percentage_bound(non_nan_indexes,atlite_lats,atlite_lons,full_atlite_data,WAD_lats,WAD_lons):
        # count as the values get added on to take the average at the end
        number_columns_in_tier = 0
        # skeleton to hold the values
        cumulative_average_values = np.zeros((len(full_atlite_data[:,0,0])))

        # loop through non-nan indexes and find the corresponding location in atlite data then cummalative average
        for count_index, data_index in enumerate(non_nan_indexes):
            print("Busy with entry: ",count_index," out of ",len(non_nan_indexes))

            # find the closest index within the atlite data:
            closest_lat_index = np.argmin(np.abs(latitude_wad[data_index[0]]-atlite_lats.values))
            closest_lon_index = np.argmin(np.abs(longitude_wad[data_index[1]]-atlite_lons.values))

            # donr need the actual value in this case:
            # # value = full_atlite_data[data_index[0]][data_index[1]]

            # Add the new column to the skeleton column
            cumulative_average_values += full_atlite_data[:, closest_lat_index, closest_lon_index]
            number_columns_in_tier += 1

        # take the average
        print("... A tier was created.")
        return cumulative_average_values/number_columns_in_tier


    print("... Generating user tier bounds.")
    print("...")

    # Convert the PERCENT_UPPER_TIER1_CAPACITY_FACTORS variable to a list of floats
    percent_upper_tier1_capacity_factors = list(map(float, PERCENT_UPPER_TIER1_CAPACITY_FACTORS.split(',')))
    percent_upper_tier2_capacity_factors = list(map(float, PERCENT_UPPER_TIER2_CAPACITY_FACTORS.split(',')))
    percent_upper_tier3_capacity_factors = list(map(float, PERCENT_UPPER_TIER3_CAPACITY_FACTORS.split(',')))
    percent_upper_tier4_capacity_factors = list(map(float, PERCENT_UPPER_TIER4_CAPACITY_FACTORS.split(',')))
    percent_upper_tier5_capacity_factors = list(map(float, PERCENT_UPPER_TIER5_CAPACITY_FACTORS.split(',')))

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

    print("... Tier bounds processed:")
    print("... Tier 1 bounds: ", min(percent_upper_tier1_capacity_factors)," - ", max(percent_upper_tier1_capacity_factors))
    print("... Tier 2 bounds: ", min(percent_upper_tier2_capacity_factors)," - ", max(percent_upper_tier2_capacity_factors))
    print("... Tier 3 bounds: ", min(percent_upper_tier3_capacity_factors)," - ", max(percent_upper_tier3_capacity_factors))
    print("... Tier 4 bounds: ", min(percent_upper_tier4_capacity_factors)," - ", max(percent_upper_tier4_capacity_factors))
    print("... Tier 5 bounds: ", min(percent_upper_tier5_capacity_factors)," - ", max(percent_upper_tier5_capacity_factors))
    print("...")

    # Find the values between the specified quantiles
    bounds_tier1 = copy.deepcopy(all_data_wad).stack(z=(WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME, WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME)).quantile([lower_percentile_tier1, upper_percentile_tier1])#, dim='z')
    bounds_tier2 = copy.deepcopy(all_data_wad).stack(z=(WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME, WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME)).quantile([lower_percentile_tier2, upper_percentile_tier2])#, dim='z')
    bounds_tier3 = copy.deepcopy(all_data_wad).stack(z=(WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME, WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME)).quantile([lower_percentile_tier3, upper_percentile_tier3])#, dim='z')
    bounds_tier4 = copy.deepcopy(all_data_wad).stack(z=(WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME, WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME)).quantile([lower_percentile_tier4, upper_percentile_tier4])#, dim='z')
    bounds_tier5 = copy.deepcopy(all_data_wad).stack(z=(WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME, WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME)).quantile([lower_percentile_tier5, upper_percentile_tier5])#, dim='z')

    print("... Quantiles generated.")
    print("... Quantile 1: ",bounds_tier1.data)
    print("... Quantile 2: ",bounds_tier2.data)
    print("... Quantile 3: ",bounds_tier3.data)
    print("... Quantile 4: ",bounds_tier4.data)
    print("... Quantile 5: ",bounds_tier5.data)
    print("...")


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

    print("... Values for WAD data bounds generated")
    print("... Tier 1: ",bottom_bound_tier1," - ",top_bound_tier1)
    print("... Tier 2: ",bottom_bound_tier2," - ",top_bound_tier2)
    print("... Tier 3: ",bottom_bound_tier3," - ",top_bound_tier3)
    print("... Tier 4: ",bottom_bound_tier4," - ",top_bound_tier4)
    print("... Tier 5: ",bottom_bound_tier5," - ",top_bound_tier5)
    print("...")

    # Use boolean indexing to select the desired indexes
    selected_indexes_WAD_tier1 = all_data_wad.where((all_data_wad>bottom_bound_tier1) & (all_data_wad<top_bound_tier1))#, drop=True)
    selected_indexes_WAD_tier2 = all_data_wad.where((all_data_wad>bottom_bound_tier2) & (all_data_wad<top_bound_tier2))#, drop=True)
    selected_indexes_WAD_tier3 = all_data_wad.where((all_data_wad>bottom_bound_tier3) & (all_data_wad<top_bound_tier3))#, drop=True)
    selected_indexes_WAD_tier4 = all_data_wad.where((all_data_wad>bottom_bound_tier4) & (all_data_wad<top_bound_tier4))#, drop=True)
    selected_indexes_WAD_tier5 = all_data_wad.where((all_data_wad>bottom_bound_tier5) & (all_data_wad<top_bound_tier5))#, drop=True)

    # print("selected_indexes_WAD_tiers")
    # print(selected_indexes_WAD_tier1)
    # print(selected_indexes_WAD_tier2)
    # print(selected_indexes_WAD_tier3)
    # print(selected_indexes_WAD_tier4)
    # print(selected_indexes_WAD_tier5)

    # get the indices that are not nan, we average on these indexes
    non_nan_indices_tier1 = np.argwhere(~np.isnan(selected_indexes_WAD_tier1.data))
    non_nan_indices_tier2 = np.argwhere(~np.isnan(selected_indexes_WAD_tier2.data))
    non_nan_indices_tier3 = np.argwhere(~np.isnan(selected_indexes_WAD_tier3.data))
    non_nan_indices_tier4 = np.argwhere(~np.isnan(selected_indexes_WAD_tier4.data))
    non_nan_indices_tier5 = np.argwhere(~np.isnan(selected_indexes_WAD_tier5.data))

    # print("Non-nan indices")
    # print(non_nan_indices_tier1,len(non_nan_indices_tier1))
    # print(non_nan_indices_tier2,len(non_nan_indices_tier2))
    # print(non_nan_indices_tier3,len(non_nan_indices_tier3))
    # print(non_nan_indices_tier4,len(non_nan_indices_tier4))
    # print(non_nan_indices_tier5,len(non_nan_indices_tier5))

    # # Generate the tiers using Atlite data:
    print("... Generating tier 1:")
    bound_tier1 = get_tier_percentage_bound(non_nan_indices_tier1,atlite_lats,atlite_lons,atlite_capacity_factors[AVG_ATLITE_DATA_VARIABLE_NAME].values,latitude_wad,longitude_wad)
    print("... Generating tier 2:")
    bound_tier2 = get_tier_percentage_bound(non_nan_indices_tier2,atlite_lats,atlite_lons,atlite_capacity_factors[AVG_ATLITE_DATA_VARIABLE_NAME].values,latitude_wad,longitude_wad)
    print("... Generating tier 3:")
    bound_tier3 = get_tier_percentage_bound(non_nan_indices_tier3,atlite_lats,atlite_lons,atlite_capacity_factors[AVG_ATLITE_DATA_VARIABLE_NAME].values,latitude_wad,longitude_wad)
    print("... Generating tier 4:")
    bound_tier4 = get_tier_percentage_bound(non_nan_indices_tier4,atlite_lats,atlite_lons,atlite_capacity_factors[AVG_ATLITE_DATA_VARIABLE_NAME].values,latitude_wad,longitude_wad)
    print("... Generating tier 5:")
    bound_tier5 = get_tier_percentage_bound(non_nan_indices_tier5,atlite_lats,atlite_lons,atlite_capacity_factors[AVG_ATLITE_DATA_VARIABLE_NAME].values,latitude_wad,longitude_wad)

    print("... All tiers created.")

    print("... Tier 1: ",bound_tier1)
    print("... Tier 2: ",bound_tier2)
    print("... Tier 3: ",bound_tier3)
    print("... Tier 4: ",bound_tier4)
    print("... Tier 5: ",bound_tier5)
    print("...")


    # Create a DataFrame
    tier_dataframe = pd.DataFrame({
        'tier_1': bound_tier1,
        'tier_2': bound_tier2,
        'tier_3': bound_tier3,
        'tier_4': bound_tier4,
        'tier_5': bound_tier5
    })

    print("... Saving tiers to csv file.")
    # check if output directories are created
    if not os.path.exists(OPTION_4_OUTPUT_FOLDER):
        os.makedirs(OPTION_4_OUTPUT_FOLDER)

    # scale capacity factors if required:
    if SCALE_CAPACITY_FACTORS.lower() == "true":
        tier_dataframe = tier_dataframe / float(MAXIMUM_CAPACITY)  # divide by the weightings
        print("\n... Capacity factors were scaled by division of maximum capacity:",MAXIMUM_CAPACITY)

    tier_dataframe.to_csv(os.path.join(OPTION_4_OUTPUT_FOLDER,BOUND_CAPACITY_FACTORS_TIME_SERIES_FILE_4),index=False)

    print("\n... Tier files for bounds capacity factors created:")
    print("...... Tier file located in: " + os.path.join(OPTION_4_OUTPUT_FOLDER,BOUND_CAPACITY_FACTORS_TIME_SERIES_FILE_4))
    print("... Note that there are only 5 tiers for this option.")


    print("\nOption_4 completed successfully!")

if __name__ == '__main__':
    # check args or load env file and run codes
    try:
        print("TRYING TO USE ARGUMENTS")
        args = parse_arguments()
        print("ARGUMENTS FOUND. USING ARGUMENTS")

        # RUN CODES
        average_bounded_capacity_factors_WAD(**vars(args))
    except Exception as e:
        print("ARGUMENTS NOT FOUND: ", e)
        try:
            print("TRYING TO LOAD ENV FILE VARIABLES")
            # Load variables from the .env file
            args = load_from_env()
            print("ENV FILE FOUND. USING ENV FILE")

            # RUN CODES
            average_bounded_capacity_factors_WAD(**args)

        except Exception as e:
            print("ENV FILE NOT FOUND: ", e)
            print("ERROR ... USER ARGS AND ENV FILE NOT FOUND, ABORTING!")
            raise ValueError("COULD NOT FIND ARGS OR LOAD ENV FILE. USER ARGS OR ENV FILE MISSING.")

    # args example use:
    # python Option_4_bound_percentage_WAD.py  --ATLITE_DUMMY_DATA True  --DUMMY_START_DATE '2023-01-01'  --DUMMY_END_DATE '2024-01-01'  --DUMMY_LATITUDE_BOTTOM -32.0  --DUMMY_LATITUDE_TOP -30.0  --DUMMY_LONGITUDE_LEFT 26.0  --DUMMY_LONGITUDE_RIGHT 28.0 --MAXIMUM_CAPACITY 50  --DATA_VARIABLE_NAME capacity_factors  --TIME_VARIABLE_NAME time  --AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION "assets/avg_atlite_capacity_factors.nc"  --AVG_ATLITE_LATITUDE_VARIABLE_NAME latitude  --AVG_ATLITE_LONGITUDE_VARIABLE_NAME longitude  --REDUCED_WAD True  --WIND_ATLAS_RESOLUTION_REDUCTION 15  --WIND_ATLAS_CAPACITY_FACTORS_HEATMAP_FILE_LOCATION "assets/wind_atlas_capacity_factors.nc"  --WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME lat  --WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME lon  --WIND_ATLAS_HEATMAP_DATA_VARIABLE_NAME Band1  --PERCENT_UPPER_TIER1_CAPACITY_FACTORS 0,10  --PERCENT_UPPER_TIER2_CAPACITY_FACTORS 10,20  --PERCENT_UPPER_TIER3_CAPACITY_FACTORS 0,40  --PERCENT_UPPER_TIER4_CAPACITY_FACTORS 60,100  --PERCENT_UPPER_TIER5_CAPACITY_FACTORS 40,60 --AVG_ATLITE_DATA_VARIABLE_NAME capacity_factors  --OPTION_4_OUTPUT_FOLDER "assets/option_4_output"  --SCALE_CAPACITY_FACTORS True  --MAXIMUM_CAPACITY 50  --BOUND_CAPACITY_FACTORS_TIME_SERIES_FILE_4 "option_4_bounded_percentage_capacity_factor_time_series.csv"
