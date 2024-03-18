"""
Purpose: Returns the upper percentage averaged capacity factors for the WIND ATLAS data.

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

import warnings


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


        # all_data_wad = all_data_wad.fillna(0)
        # print(atlite_capacity_factors_avg)
        # print(all_data_wad)



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
        # top_percentage = copy.deepcopy(atlite_capacity_factors_avg).stack(z=(os.environ.get("AVG_ATLITE_LATITUDE_VARIABLE_NAME"), os.environ.get("AVG_ATLITE_LONGITUDE_VARIABLE_NAME"))).quantile(1.0 - float(os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS_2"))/100)
        top_percentage = copy.deepcopy(all_data_wad).stack(z=(os.environ.get("WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME"), os.environ.get("WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME"))).quantile(1.0 - float(os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS_2"))/100)
        print(top_percentage)


        # Use boolean indexing to select the desired indexes
        # selected_indexes = atlite_capacity_factors_avg.where(atlite_capacity_factors_avg>top_percentage)#, drop=True)
        selected_indexes = all_data_wad.where(all_data_wad>top_percentage)#, drop=True)
        print(selected_indexes)

        # get lats/lons
        latitudes = selected_indexes[os.environ.get(("WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME"))].values
        longitudes = selected_indexes[os.environ.get(("WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME"))].values

        # empty shell to store the lats/lons and the data, then average them later
        # check if output directories are created
        if not os.path.exists(os.environ.get('OPTION_2_OUTPUT_FOLDER')):
            os.makedirs(os.environ.get('OPTION_2_OUTPUT_FOLDER'))

        # Check if the file exists
        print(os.environ.get('OPTION_2_OUTPUT_FOLDER'))
        print(os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS_TIME_SERIES_FILE_ATLITE_2"))
        tiers = os.path.join(os.environ.get('OPTION_2_OUTPUT_FOLDER'),os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS_TIME_SERIES_FILE_2"))
        locations_wad = os.path.join(os.environ.get('OPTION_2_OUTPUT_FOLDER'),os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE_WAD_2"))
        locations_atlite=os.path.join(os.environ.get('OPTION_2_OUTPUT_FOLDER'),os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE_ATLITE_2"))
        if not os.path.exists(tiers):
            # Create an empty DataFrame
            df = pd.DataFrame()
            # Save the DataFrame to the CSV file
            df.to_csv(tiers, index=False)
            print(f"Created empty CSV file: {tiers}")

        if not os.path.exists(locations_atlite):
            # Create an empty DataFrame
            df = pd.DataFrame(columns=['latitude', 'longitude','average_capacity_factor'])
            # Save the DataFrame to the CSV file
            df.to_csv(locations_atlite, index=False)
            print(f"Created empty CSV file: {locations_atlite}")

        if not os.path.exists(locations_wad):
            # Create an empty DataFrame
            df = pd.DataFrame(columns=['latitude', 'longitude','average_capacity_factor'])
            # Save the DataFrame to the CSV file
            df.to_csv(locations_wad, index=False)
            print(f"Created empty CSV file: {locations_wad}")


        # lat_lon_df_atlite = pd.DataFrame(columns=['latitude', 'longitude','average_capacity_factor'])
        # lat_lon_df_wad = pd.DataFrame(columns=['latitude', 'longitude','average_capacity_factor'])
        # tiers_raw_df = pd.DataFrame()

        # loop through and find if nan or data, for wad data
        print("Lens: ",len(latitudes),len(longitudes))
        for lat in range(len(latitudes)):
            print(lat,"/",len(latitudes))
            for lon in range(len(longitudes)):
                value = selected_indexes.data[lat][lon]
                if np.isnan(value):
                    continue
                else:
                    # add data to the data frame
                    # lat/lon wad
                    # lat_lon_df_wad.loc[len(lat_lon_df_wad)] = [latitudes[lat],longitudes[lon],value]
                    df_wad_loactions = pd.read_csv(locations_wad)
                    df_wad_loactions.loc[len(df_wad_loactions)] = [latitudes[lat],longitudes[lon],value]
                    df_wad_loactions.to_csv(locations_wad,index=False)

                    # get lat lon corresponding to atlite data:
                    closest_lat_index = np.argmin(np.abs(latitudes[lat]-atlite_lats.values))
                    closest_lon_index = np.argmin(np.abs(longitudes[lon]-atlite_lons.values))

                    # lat/lon atlite
                    # lat_lon_df_atlite.loc[len(lat_lon_df_atlite)] = [atlite_lats.values[closest_lat_index],atlite_lons.values[closest_lon_index],atlite_capacity_factors_avg.data[closest_lat_index,closest_lon_index]]
                    df_atlite_loactions = pd.read_csv(locations_atlite)
                    df_atlite_loactions.loc[len(df_atlite_loactions)] = [atlite_lats.values[closest_lat_index],atlite_lons.values[closest_lon_index],atlite_capacity_factors_avg.data[closest_lat_index,closest_lon_index]]
                    df_atlite_loactions.to_csv(locations_atlite, index=False)

                    # timeseries
                    # Determine the next number for the new column name
                    try:
                        # Open CSV file with pandas
                        tiers_raw_df = pd.read_csv(tiers)
                    except pd.errors.EmptyDataError:
                        # If the file is empty, create an empty DataFrame
                        tiers_raw_df = pd.DataFrame()

                    next_column_number = len(tiers_raw_df.columns) + 1
                    # Create a new column name
                    new_column_name = f'pre_tier_{next_column_number}'
                    # Add the new column to the DataFrame
                    # tiers_raw_df[new_column_name] = atlite_capacity_factors[os.environ.get("DATA_VARIABLE_NAME")].values[:,atlite_lats.values[closest_lat_index],atlite_lons.values[closest_lon_index]]
                    tiers_raw_df[new_column_name] = atlite_capacity_factors[os.environ.get("DATA_VARIABLE_NAME")].values[:,closest_lat_index,closest_lon_index]
                    tiers_raw_df.to_csv(tiers,index=False)
                    # print(value)

        # get the final tier and save it
        tiers_raw_df = pd.read_csv(tiers)
        tiers_raw_df['average_tier_final'] = tiers_raw_df.mean(axis=1)
        tiers_raw_df.to_csv(tiers, index=False)

        # tiers_raw_df.to_csv(os.path.join(os.environ.get('OPTION_2_OUTPUT_FOLDER'),os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS_TIME_SERIES_FILE_ATLITE_2")))
        # lat_lon_df_wad.to_csv(os.path.join(os.environ.get('OPTION_2_OUTPUT_FOLDER'),os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE_WAD_2")))
        # lat_lon_df_atlite.to_csv(os.path.join(os.environ.get('OPTION_2_OUTPUT_FOLDER'),os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE_2")))

        print("... Tier files for top "+os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS_2")+" capacity factors created:")
        print("...... Location file located in: "+os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE_2"))
        print("...... Tier file located in: "+os.environ.get("PERCENT_UPPER_CAPACITY_FACTORS_TIME_SERIES_FILE_2"))
        print("... Note that averaged tier is in average_tier_final column.")

        print("Option_2 completed successfully!")


if __name__ == '__main__':

    average_capacity_factors_WAD()
