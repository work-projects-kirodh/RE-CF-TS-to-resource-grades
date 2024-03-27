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

import Option_Support_Functions as support_functions

# Load variables from the .env file
load_dotenv()


def average_bounded_capacity_factors_WAD():
    # # Code block where you want to suppress warnings
    # with warnings.catch_warnings():
    #     warnings.simplefilter("ignore")

    # average the capacity factors according to time:
    atlite_capacity_factors, atlite_capacity_factors_avg = support_functions.create_average_capacity_factor_file_atlite()
    atlite_lats = atlite_capacity_factors[os.environ.get('AVG_ATLITE_LATITUDE_VARIABLE_NAME')]
    atlite_lons = atlite_capacity_factors[os.environ.get('AVG_ATLITE_LONGITUDE_VARIABLE_NAME')]
    print("... Read averaged atlite capacity factor data.")

    if os.environ.get('REDUCED_WAD').lower() == "true":
        # open the WAD data
        latitude_wad,longitude_wad,all_data_wad = support_functions.read_wind_atlas_data_reduced()
    else:
        # open the WAD data
        latitude_wad, longitude_wad, all_data_wad = support_functions.read_wind_atlas_data_full()


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

    print("... Tier bounds processed:")
    print("... Tier 1 bounds: ", min(percent_upper_tier1_capacity_factors)," - ", max(percent_upper_tier1_capacity_factors))
    print("... Tier 2 bounds: ", min(percent_upper_tier2_capacity_factors)," - ", max(percent_upper_tier2_capacity_factors))
    print("... Tier 3 bounds: ", min(percent_upper_tier3_capacity_factors)," - ", max(percent_upper_tier3_capacity_factors))
    print("... Tier 4 bounds: ", min(percent_upper_tier4_capacity_factors)," - ", max(percent_upper_tier4_capacity_factors))
    print("... Tier 5 bounds: ", min(percent_upper_tier5_capacity_factors)," - ", max(percent_upper_tier5_capacity_factors))
    print("...")

    # Find the values between the specified quantiles
    bounds_tier1 = copy.deepcopy(all_data_wad).stack(z=(os.environ.get("WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME"), os.environ.get("WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME"))).quantile([lower_percentile_tier1, upper_percentile_tier1])#, dim='z')
    bounds_tier2 = copy.deepcopy(all_data_wad).stack(z=(os.environ.get("WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME"), os.environ.get("WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME"))).quantile([lower_percentile_tier2, upper_percentile_tier2])#, dim='z')
    bounds_tier3 = copy.deepcopy(all_data_wad).stack(z=(os.environ.get("WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME"), os.environ.get("WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME"))).quantile([lower_percentile_tier3, upper_percentile_tier3])#, dim='z')
    bounds_tier4 = copy.deepcopy(all_data_wad).stack(z=(os.environ.get("WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME"), os.environ.get("WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME"))).quantile([lower_percentile_tier4, upper_percentile_tier4])#, dim='z')
    bounds_tier5 = copy.deepcopy(all_data_wad).stack(z=(os.environ.get("WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME"), os.environ.get("WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME"))).quantile([lower_percentile_tier5, upper_percentile_tier5])#, dim='z')

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
    bound_tier1 = get_tier_percentage_bound(non_nan_indices_tier1,atlite_lats,atlite_lons,atlite_capacity_factors[os.environ.get("AVG_ATLITE_DATA_VARIABLE_NAME")].values,latitude_wad,longitude_wad)
    print("... Generating tier 2:")
    bound_tier2 = get_tier_percentage_bound(non_nan_indices_tier2,atlite_lats,atlite_lons,atlite_capacity_factors[os.environ.get("AVG_ATLITE_DATA_VARIABLE_NAME")].values,latitude_wad,longitude_wad)
    print("... Generating tier 3:")
    bound_tier3 = get_tier_percentage_bound(non_nan_indices_tier3,atlite_lats,atlite_lons,atlite_capacity_factors[os.environ.get("AVG_ATLITE_DATA_VARIABLE_NAME")].values,latitude_wad,longitude_wad)
    print("... Generating tier 4:")
    bound_tier4 = get_tier_percentage_bound(non_nan_indices_tier4,atlite_lats,atlite_lons,atlite_capacity_factors[os.environ.get("AVG_ATLITE_DATA_VARIABLE_NAME")].values,latitude_wad,longitude_wad)
    print("... Generating tier 5:")
    bound_tier5 = get_tier_percentage_bound(non_nan_indices_tier5,atlite_lats,atlite_lons,atlite_capacity_factors[os.environ.get("AVG_ATLITE_DATA_VARIABLE_NAME")].values,latitude_wad,longitude_wad)

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
    if not os.path.exists(os.environ.get('OPTION_4_OUTPUT_FOLDER')):
        os.makedirs(os.environ.get('OPTION_4_OUTPUT_FOLDER'))

    # scale capacity factors if required:
    if os.environ.get('SCALE_CAPACITY_FACTORS').lower() == "true":
        tier_dataframe = tier_dataframe / float(os.environ.get("MAXIMUM_CAPACITY"))  # divide by the weightings
        print("\n... Capacity factors were scaled by division of maximum capacity:",os.environ.get("MAXIMUM_CAPACITY"))

    tier_dataframe.to_csv(os.path.join(os.environ.get('OPTION_4_OUTPUT_FOLDER'),os.environ.get("BOUND_CAPACITY_FACTORS_TIME_SERIES_FILE_4")),index=False)

    print("\n... Tier files for bounds capacity factors created:")
    print("...... Tier file located in: " + os.path.join(os.environ.get('OPTION_4_OUTPUT_FOLDER'),os.environ.get("BOUND_CAPACITY_FACTORS_TIME_SERIES_FILE_4")))
    print("... Note that there are only 5 tiers for this option.")


    print("\nOption_4 completed successfully!")

if __name__ == '__main__':

    average_bounded_capacity_factors_WAD()
