"""
Purpose: Support functions for generating tiers.

Author: Kirodh Boodhraj
"""
import os
import xarray as xr
import numpy as np
import temporary_data as temp_data
from dotenv import load_dotenv
import rasterio
import folium

# Load variables from the .env file
load_dotenv()

def create_average_capacity_factor_file_atlite():
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

    return atlite_capacity_factors, atlite_capacity_factors_avg


def read_wind_atlas_data_full():
    # get down scaling resolution of wind atlas netcdf i.e. number of points to skip for lat lon values in array, to make things render faster
    wind_atlas_resolution_reduction = int(os.environ.get("WIND_ATLAS_RESOLUTION_REDUCTION"))
    # open wind atlas netcdf
    wind_atlas_netcdf = xr.open_dataset(os.environ.get("WIND_ATLAS_CAPACITY_FACTORS_HEATMAP_FILE_LOCATION"))

    # # Select every wind_atlas_resolution_reduction latitude and longitude along with capacity_factor
    # capacity_factor_subset = wind_atlas_netcdf.sel(
    #     lat=wind_atlas_netcdf.lat.values[::wind_atlas_resolution_reduction],
    #     lon=wind_atlas_netcdf.lon.values[::wind_atlas_resolution_reduction])

    # Access the capacity_factor variable from the subset
    latitude_wa = wind_atlas_netcdf[os.environ.get("WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME")].values.astype(float)
    longitude_wa = wind_atlas_netcdf[os.environ.get("WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME")].values.astype(float)
    all_data_wa = wind_atlas_netcdf[os.environ.get("WIND_ATLAS_HEATMAP_DATA_VARIABLE_NAME")] #.values.astype(float)
    # all_data_wa[np.isnan(all_data_wa)] = 0.0  # Replace NaN with 0.0, you can choose a different value if needed
    # lon_wa, lat_wa = np.meshgrid(longitude_wa, latitude_wa)
    return latitude_wa,longitude_wa,all_data_wa


def read_wind_atlas_data_reduced():
    # get down scaling resolution of wind atlas netcdf i.e. number of points to skip for lat lon values in array, to make things render faster
    wind_atlas_resolution_reduction = int(os.environ.get("WIND_ATLAS_RESOLUTION_REDUCTION"))
    # open wind atlas netcdf
    wind_atlas_netcdf = xr.open_dataset(os.environ.get("WIND_ATLAS_CAPACITY_FACTORS_HEATMAP_FILE_LOCATION"))

    # Select every wind_atlas_resolution_reduction latitude and longitude along with capacity_factor
    capacity_factor_subset = wind_atlas_netcdf.sel(
        lat=wind_atlas_netcdf.lat.values[::wind_atlas_resolution_reduction],
        lon=wind_atlas_netcdf.lon.values[::wind_atlas_resolution_reduction])

    # Access the capacity_factor variable from the subset
    latitude_wa = capacity_factor_subset[os.environ.get("WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME")].values.astype(float)
    longitude_wa = capacity_factor_subset[os.environ.get("WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME")].values.astype(float)
    values_wa = capacity_factor_subset[os.environ.get("WIND_ATLAS_HEATMAP_DATA_VARIABLE_NAME")] #.values.astype(float)
    # values_wa[np.isnan(values_wa)] = 0.0  # Replace NaN with 0.0, you can choose a different value if needed
    # lon_wa, lat_wa = np.meshgrid(longitude_wa, latitude_wa)

    return latitude_wa,longitude_wa,values_wa


def read_masks_as_folium_layers():
    # Read the tiff mask files and return as folium map layers

    # Path to your TIFF folder
    tiff_folder_path = os.environ.get("MASKS_FOLDER")

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



