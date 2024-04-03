"""
Purpose: Support functions for generating tiers.

Author: Kirodh Boodhraj
"""
import os
import xarray as xr
import numpy as np
import pandas as pd
from dotenv import load_dotenv
import rasterio
import folium

from branca.colormap import linear


# Load variables from the .env file
load_dotenv()


# Atlite data temporary data functions
# Function to generate random data
def generate_random_data(latitudes, longitudes,MAXIMUM_CAPACITY):
    maximum_capacity = MAXIMUM_CAPACITY # MW
    return np.random.rand(len(latitudes), len(longitudes)),maximum_capacity

def create_temporary_atlite_dataset(DUMMY_START_DATE,DUMMY_END_DATE,DUMMY_LATITUDE_BOTTOM,DUMMY_LATITUDE_TOP,DUMMY_LONGITUDE_LEFT,DUMMY_LONGITUDE_RIGHT,MAXIMUM_CAPACITY,DATA_VARIABLE_NAME):
    # Step 1: Create hourly date times in a Pandas series
    hourly_date_times = pd.date_range(start=DUMMY_START_DATE, end=DUMMY_END_DATE, freq='H')

    """ temporary fix start """
    # Step 2: Create equally spaced intervals of 0.1 degrees between latitudes and longitudes
    latitude_intervals = np.arange(float(DUMMY_LATITUDE_BOTTOM), float(DUMMY_LATITUDE_TOP), 0.1)
    longitude_intervals = np.arange(float(DUMMY_LONGITUDE_LEFT), float(DUMMY_LONGITUDE_RIGHT), 0.1)

    # Step 3: Create an empty Xarray dataset
    atlite_capacity_factors = xr.Dataset(
        {
            'capacity_factors': (['time', 'latitude', 'longitude'], np.zeros((len(hourly_date_times), len(latitude_intervals), len(longitude_intervals))))
        },
        coords={
            'time': hourly_date_times,
            'latitude': latitude_intervals,
            'longitude': longitude_intervals
        }
    )
    """ temporary fix end """

    # Step 4: Loop through each hourly timestep and generate random data
    for i, time in enumerate(hourly_date_times):
        """ temporary fix """
        capacity_factors, maximum_capacity = generate_random_data(latitude_intervals, longitude_intervals,MAXIMUM_CAPACITY)
        atlite_capacity_factors[DATA_VARIABLE_NAME][i, :, :] = capacity_factors
        """ temporary fix """

    # print(atlite_capacity_factors["latitude"],atlite_capacity_factors["longitude"])

    return atlite_capacity_factors


def stitch_Atlite_data(ATLITE_CAPACITY_FACTORS_FOLDERS,DUMMY_START_DATE,DATA_VARIABLE_NAME):
    # Split the folder string by commas to get individual folder paths
    folders = ATLITE_CAPACITY_FACTORS_FOLDERS.split(',')

    # # Create an empty list to store all data arrays before stitchingthem together in xarray
    data_array = []

    def sort_filenames(filename):
        # Extract the numerical part of the filename, because it sorts 0, 1, 10, 100 etc. but we want 1, 2, 3, 4 ...
        return int(filename.split('_')[-1].split('.')[0])

    # Iterate through each folder
    for index,folder in enumerate(folders):
        print("... Busy reading files of folder ",index+1, " out of ",len(folders))
        # Get all CSV files in the folder
        csv_files = [file for file in os.listdir(folder) if file.endswith('.csv')]

        # Sort CSV files numerically
        csv_files.sort(key=sort_filenames)

        # Iterate through each CSV file
        for csv_file in csv_files:
            # Read CSV file into a pandas DataFrame
            df = pd.read_csv(os.path.join(folder, csv_file), header=None)
            # print(df)

            # Extract longitude from the first row and latitude from the first column
            lon = [float(x) for x in df.iloc[0,:].values[1:]] # get the first row, then get values otherwise same name as dimension error, remove the first value from the data as it is the header, and type cast all to float because the header makes it all strings and not numbers
            lat = [float(x) for x in df.iloc[:,0].values[1:]]
            # print(lon, lat)
            # 1/0

            # Remove the first row and column (latitude and longitude)
            df = df.iloc[1:, 1:]
            # get the remaining values
            data_slice = df.values
            # append to list before pulling all values together
            data_array.append(data_slice)


    # Concatenate the list of arrays along a new axis
    concatenated_data = np.stack(data_array, axis=-1)
    # print(concatenated_data.shape)

    # Combine all data arrays into a single xarray dataset
    print("Stitching all data together ...")
    Atlite_data = xr.Dataset(
        {
            DATA_VARIABLE_NAME: (["time", "latitude", "longitude"], np.transpose(concatenated_data, (2, 0, 1))),
        },
        coords={
            "time": range(0, len(concatenated_data[0,0,:])),
            "latitude": lat,
            "longitude": lon,
        },
    )

    # # Save the xarray dataset to netCDF format
    # ds.to_netcdf('avg_data.nc')

    return Atlite_data

# Atlite data
def create_average_capacity_factor_file_atlite(ATLITE_DUMMY_DATA, ATLITE_CAPACITY_FACTORS_FOLDERS,DUMMY_START_DATE,DUMMY_END_DATE,DUMMY_LATITUDE_BOTTOM,DUMMY_LATITUDE_TOP,DUMMY_LONGITUDE_LEFT,DUMMY_LONGITUDE_RIGHT,MAXIMUM_CAPACITY,DATA_VARIABLE_NAME,TIME_VARIABLE_NAME,AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION):
    # Read in the capacity factors after running WP3 codes:
    if ATLITE_DUMMY_DATA.lower() == 'true':
        ## use temp data for now:
        atlite_capacity_factors = create_temporary_atlite_dataset(DUMMY_START_DATE,DUMMY_END_DATE,DUMMY_LATITUDE_BOTTOM,DUMMY_LATITUDE_TOP,DUMMY_LONGITUDE_LEFT,DUMMY_LONGITUDE_RIGHT,MAXIMUM_CAPACITY,DATA_VARIABLE_NAME)
        print("... Opened DUMMY atlite capacity factor data.")
    else:
        # use real data
        atlite_capacity_factors = stitch_Atlite_data(ATLITE_CAPACITY_FACTORS_FOLDERS,DUMMY_START_DATE,DATA_VARIABLE_NAME)
        print("... Opened atlite capacity factor data.")

    # average the capacity factors according to time:
    atlite_capacity_factors_avg = atlite_capacity_factors[DATA_VARIABLE_NAME].mean(dim=TIME_VARIABLE_NAME)
    print("... Averaged atlite capacity factor data.")

    # save file to assets folder:
    atlite_capacity_factors_avg.to_netcdf(AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION)
    print("... Saved average atlite capacity factor data.")

    return atlite_capacity_factors, atlite_capacity_factors_avg


def read_wind_atlas_data_full(WIND_ATLAS_CAPACITY_FACTORS_HEATMAP_FILE_LOCATION,WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME,WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME,WIND_ATLAS_HEATMAP_DATA_VARIABLE_NAME):
    # open wind atlas netcdf
    wind_atlas_netcdf = xr.open_dataset(WIND_ATLAS_CAPACITY_FACTORS_HEATMAP_FILE_LOCATION)

    # # Select every wind_atlas_resolution_reduction latitude and longitude along with capacity_factor
    # capacity_factor_subset = wind_atlas_netcdf.sel(
    #     lat=wind_atlas_netcdf.lat.values[::wind_atlas_resolution_reduction],
    #     lon=wind_atlas_netcdf.lon.values[::wind_atlas_resolution_reduction])

    # Access the capacity_factor variable from the subset
    latitude_wa = wind_atlas_netcdf[WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME].values.astype(float)
    longitude_wa = wind_atlas_netcdf[WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME].values.astype(float)
    all_data_wa = wind_atlas_netcdf[WIND_ATLAS_HEATMAP_DATA_VARIABLE_NAME] #.values.astype(float)
    # all_data_wa[np.isnan(all_data_wa)] = 0.0  # Replace NaN with 0.0, you can choose a different value if needed
    # lon_wa, lat_wa = np.meshgrid(longitude_wa, latitude_wa)
    return latitude_wa,longitude_wa,all_data_wa


def read_wind_atlas_data_reduced(WIND_ATLAS_RESOLUTION_REDUCTION,WIND_ATLAS_CAPACITY_FACTORS_HEATMAP_FILE_LOCATION,WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME,WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME,WIND_ATLAS_HEATMAP_DATA_VARIABLE_NAME):
    # get down scaling resolution of wind atlas netcdf i.e. number of points to skip for lat lon values in array, to make things render faster
    wind_atlas_resolution_reduction = int(WIND_ATLAS_RESOLUTION_REDUCTION)
    # open wind atlas netcdf
    wind_atlas_netcdf = xr.open_dataset(WIND_ATLAS_CAPACITY_FACTORS_HEATMAP_FILE_LOCATION)

    # Select every wind_atlas_resolution_reduction latitude and longitude along with capacity_factor
    capacity_factor_subset = wind_atlas_netcdf.sel(
        lat=wind_atlas_netcdf.lat.values[::wind_atlas_resolution_reduction],
        lon=wind_atlas_netcdf.lon.values[::wind_atlas_resolution_reduction])

    # Access the capacity_factor variable from the subset
    latitude_wa = capacity_factor_subset[WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME].values.astype(float)
    longitude_wa = capacity_factor_subset[WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME].values.astype(float)
    values_wa = capacity_factor_subset[WIND_ATLAS_HEATMAP_DATA_VARIABLE_NAME] #.values.astype(float)
    # values_wa[np.isnan(values_wa)] = 0.0  # Replace NaN with 0.0, you can choose a different value if needed
    # lon_wa, lat_wa = np.meshgrid(longitude_wa, latitude_wa)

    return latitude_wa,longitude_wa,values_wa

# option 5 and 6: read in the masks single band tif files
def read_masks_as_folium_layers(MASKS_FOLDER):
    # Read the tiff mask files and return as folium map layers

    # Path to your TIFF folder
    tiff_folder_path = MASKS_FOLDER

    # List all files in the folder
    tif_files = [f for f in os.listdir(tiff_folder_path) if f.endswith('.tif')]

    # empty list for holding map layers
    final_layers = []

    # Loop through each TIFF file
    for index,tif_file in enumerate(tif_files):
        print("------------------------")
        print("Reading mask file: ",tif_file," : ",index+1," out of ",len(tif_files))
        # Full path to the TIFF file
        tif_file_path = os.path.join(tiff_folder_path, tif_file)

        # Open the TIFF file
        with rasterio.open(tif_file_path) as src:
            # get the data
            tiff_data = src.read(1)  # Assuming it's a single band TIFF
            # Get the bounds (extent) of the TIFF file
            tiff_bounds = src.bounds

        # # Doesnt seem to work,  Check if the raster is classified based on the number of unique values
        # #   if classified, then we must skip this one
        # unique_values = len(np.unique(tiff_data))
        #
        # # Threshold for considering a raster as classified (adjust as needed)
        # threshold = 1  # For example, if a raster has less than 10 unique values, it's likely classified
        #
        # if unique_values <= threshold:
        #     print(f"{tif_file} is likely classified and will be excluded.")
        #     continue  # Skip further processing for classified rasters

        # Specify the data type explicitly
        tiff_data = tiff_data.astype(float)  # Convert to float64
        tiff_data[np.isnan(tiff_data)] = 0.0  # Replace NaN with 0.0, you can choose a different value if needed
        # print(tiff_data)
        # # Dont know if needed Normalize the data to range between 0 and 1
        # tiff_data = (tiff_data - np.min(tiff_data)) / (np.max(tiff_data) - np.min(tiff_data))

        # Extract the bounds
        tiff_bottom = tiff_bounds.bottom
        tiff_left = tiff_bounds.left
        tiff_top = tiff_bounds.top
        tiff_right = tiff_bounds.right

        print("Extent of the TIFF file",tif_file,":")
        print("Bottom:", tiff_bottom)
        print("Left:", tiff_left)
        print("Top:", tiff_top)
        print("Right:", tiff_right)
        print("------------------------\n")

        # generate the map layers
        # step 1: make layer group:
        masks_layer_group = folium.FeatureGroup(name='Mask_'+str(index)+":"+tif_file)
        # step 2: create layer
        # Create a colormap
        colormap = 'YlGnBu'  # Example, you can change it to any colormap available in matplotlib
        colormap = linear.YlGnBu_09.scale(np.min(tiff_data), np.max(tiff_data))
        colormap.caption = 'Values'

        # Add the TIFF layer to the map
        wind_atlas_tiff_overlay = folium.raster_layers.ImageOverlay(
            image=tiff_data,
            bounds=[[tiff_bottom, tiff_left], [tiff_top, tiff_right]],
            opacity=0.5,
            interactive=True,
            mercator_project=True,  # Make sure to specify the projection as Mercator
            colormap=colormap,
        )
        # step 3: add layer to layer group
        wind_atlas_tiff_overlay.add_to(masks_layer_group)


        # step 4: append this layer to a list for returning
        final_layers.append(masks_layer_group)

    return final_layers

# if __name__ == '__main__':
#     test_stitch = stitch_Atlite_data("atlite_output_data\output_month_1_Jan_2023\hourly_capacity_factors,atlite_output_data\output_month_2_Jan_2023\hourly_capacity_factors,atlite_output_data\output_month_3_Jan_2023\hourly_capacity_factors,atlite_output_data\output_month_4_Jan_2023\hourly_capacity_factors,atlite_output_data\output_month_5_Jan_2023\hourly_capacity_factors,atlite_output_data\output_month_6_Jan_2023\hourly_capacity_factors,atlite_output_data\output_month_7_Jan_2023\hourly_capacity_factors,atlite_output_data\output_month_8_Jan_2023\hourly_capacity_factors,atlite_output_data\output_month_9_Jan_2023\hourly_capacity_factors,atlite_output_data\output_month_10_Jan_2023\hourly_capacity_factors,atlite_output_data\output_month_11_Jan_2023\hourly_capacity_factors,atlite_output_data\output_month_12_Jan_2023\hourly_capacity_factors",'2023-01-01',"capacity_factors")
#     # test_stitch = stitch_Atlite_data("atlite_output_data\output_month_9_Jan_2023\hourly_capacity_factors,atlite_output_data\output_month_10_Jan_2023\hourly_capacity_factors,atlite_output_data\output_month_11_Jan_2023\hourly_capacity_factors,atlite_output_data\output_month_12_Jan_2023\hourly_capacity_factors",'2023-01-01',"capacity_factors")
#     print(test_stitch)

