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

import Option_Support_Functions as support_functions

# Load variables from the .env file
load_dotenv()

def average_capacity_factors_WAD():
    # Code block where you want to suppress warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

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

        # Save top % capacity factors and generate a time series from that
        print("... Generating time series from top "+os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS_2")+" capacity factors")
        try:
            check_percentage = float(os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS_2"))
            if check_percentage < 0:
                ValueError("The percentage is less than 0. Only 0-100 allowed.")
            if check_percentage > 100:
                ValueError("The percentage is larger than 100. Only 0-100 allowed.")
        except Exception as e:
            ValueError("The percentage is not a number. Only 0-100 allowed.")
        # Find the top % values from the temporal average
        top_percentage = copy.deepcopy(all_data_wad).stack(z=(os.environ.get("WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME"), os.environ.get("WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME"))).quantile(1.0 - float(os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS_2"))/100)
        # print(top_percentage)

        # Use boolean indexing to select the desired indexes
        selected_indexes = all_data_wad.where(all_data_wad>top_percentage)#, drop=True)
        # print(selected_indexes)

        # get lats/lons
        latitudes = selected_indexes[os.environ.get(("WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME"))].values
        longitudes = selected_indexes[os.environ.get(("WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME"))].values

        non_nan_indices = np.argwhere(~np.isnan(selected_indexes.data))
        # print(len(non_nan_indices))

        # empty shell to store the lats/lons and the data, then average them later
        # check if output directories are created
        if not os.path.exists(os.environ.get('OPTION_2_OUTPUT_FOLDER')):
            os.makedirs(os.environ.get('OPTION_2_OUTPUT_FOLDER'))

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
            new_column_name = f'pre_tier_{next_column_number}'
            # Add the new column to the DataFrame
            tiers_raw_df[new_column_name] = atlite_capacity_factors[os.environ.get("DATA_VARIABLE_NAME")].values[:,closest_lat_index,closest_lon_index]

        # # get the final tier and save it
        tiers_raw_df['average_tier_final'] = tiers_raw_df.mean(axis=1)

        # save to csv files
        tiers_raw_df.to_csv(os.path.join(os.environ.get('OPTION_2_OUTPUT_FOLDER'),os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS_TIME_SERIES_FILE_2")))
        lat_lon_df_wad.to_csv(os.path.join(os.environ.get('OPTION_2_OUTPUT_FOLDER'),os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE_WAD_2")))
        lat_lon_df_atlite.to_csv(os.path.join(os.environ.get('OPTION_2_OUTPUT_FOLDER'),os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE_ATLITE_2")))

        print("... Tier files for top "+os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS_2")+" capacity factors created:")
        print("...... ATLITE Location file located in: "+os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE_ATLITE_2"))
        print("...... WIND ATLAS DATA Location file located in: "+os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE_WAD_2"))
        print("...... Tier file located in: "+os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS_TIME_SERIES_FILE_2"))
        print("... Note that averaged tier is in average_tier_final column.")

        print("Option_2 completed successfully!")


if __name__ == '__main__':

    average_capacity_factors_WAD()
