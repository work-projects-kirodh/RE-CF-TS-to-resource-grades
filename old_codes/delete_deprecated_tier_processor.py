# this script is to generate the tiers for capacity factors


""" The algorithm """
# step 1: get hourly capacity factor map
# step 2: average on time
# step 2.5: use world atlas capacity factor
# step 3:show user outputs, so they can decide on tier bins --> manual step
# step 4: obtain the best locations according to bins to get tiers
# step 5: extract all locations hourly for each tier
# step 6: weighted average for all locations per tier, per hourly timestep

# Author Kirodh Boodhraj
# November 2023

import pandas as pd
import numpy as np
import xarray as xr
import rasterio

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import geopandas as gpd
from rasterio.plot import show
from shapely.geometry import Polygon

def user_area_selection(atlite_data,world_atlas_data):
    # create map where user can select the tier areas

    if world_atlas_data is not None:
        # add this data to the plot as the main data for area selection
        pass

    from urllib.request import urlopen
    import json
    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        counties = json.load(response)

    df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv",
                     dtype={"fips": str})

    import plotly.express as px

    fig = px.choropleth_mapbox(df, geojson=counties, locations='fips', color='unemp',
                               color_continuous_scale="Viridis",
                               range_color=(0, 12),
                               mapbox_style="carto-positron",
                               zoom=3, center={"lat": 37.0902, "lon": -95.7129},
                               opacity=0.5,
                               labels={'unemp': 'unemployment rate'}
                               )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.show()

    # Load the TIFF file
    tiff_file = "path/to/your/tiff/file.tif"
    dataset = world_atlas_data # rasterio.open(tiff_file)

    # Create a GeoDataFrame with the bounds of the TIFF file
    # bounds = gpd.GeoDataFrame(geometry=[dataset.bounds.polygon])

    # Create a subplot with a scatter plot (for point selection) and the raster
    fig = make_subplots(rows=1, cols=2, column_widths=[0.2, 0.8], subplot_titles=["Click Points", "Map"])

    # Scatter plot for point selection
    scatter_fig = go.FigureWidget(make_subplots(rows=1, cols=1))
    scatter_fig.add_trace(go.Scattergeo(mode="markers"))
    scatter_fig.update_geos(showland=True, landcolor="rgb(255, 255, 255)")

    # Add the raster to the map
    # show(dataset, ax=fig, cmap="viridis") #, transform=dataset.transform)

    # Update the layout for a better map view
    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=5,  # Adjust zoom level
        mapbox_center={"lat": -30, "lon": 25},  # Center the map over South Africa
    )

    # Add a callback for point selection
    selected_points = []

    def update_point(trace, points, selector):
        global selected_points
        selected_points = scatter_fig.data[0].selectedpoints
        print("Selected Points:", selected_points)

    scatter_fig.data[0].on_selection(update_point)

    # Show the subplot
    fig.add_trace(scatter_fig.data[0])
    fig.update_geos(fitbounds="locations", visible=False)

    fig.show()

    # get tier areas and return
    tier_areas = None
    return tier_areas

# TODO:(OPTIONAL) correction for atlite and world atlas data
def world_atlas_atlite_correction(atlite_data,world_atlas_data):
    # do something here ...
    return atlite_data,world_atlas_data

# step 2 & 2.5:
def create_capacity_factor_selection_creteria(atlite_capacity_factors,maximum_capacity,world_atlas_capacity_factor_file,average=True):
    if average:
        print("Using average layers as selection area, Atlite")
        capacity_factor_selection_layer = atlite_capacity_factors["capacity_factors"].mean(dim='time')
    else: # use first layer, by default
        print("Using first layer as selection area, Atlite")
        capacity_factor_selection_layer = atlite_capacity_factors["capacity_factors"][0]

    if world_atlas_capacity_factor_file is not None:
        # use this data for the average instead of the atlite
        # TODO: open file
        # world_atlas_selection_data = open(world_atlas_capacity_factor_file)
        # Target latitude and longitude
        target_lat, target_lon = -35.4, 30.1

        # Open the GeoTIFF file
        with rasterio.open(world_atlas_capacity_factor_file) as world_atlas_selection_data:
            # Convert target latitude and longitude to pixel coordinates
            target_x, target_y = world_atlas_selection_data.index(target_lon, target_lat)
            print("targets:: ",target_x, target_y)
            # Read pixel value at the target coordinates for a specific band (e.g., band 1)
            world_atlas_selection_data = world_atlas_selection_data.read(1)
            # target_value = world_atlas_selection_data[int(target_y), int(target_x)]
            # print("World atlas target::",world_atlas_selection_data[5000,2000:8000],world_atlas_selection_data.shape)
        # TODO (OPTIONAL) correction factor algorithm goes here
        atlite_capacity_factors,world_atlas_selection_data = world_atlas_atlite_correction(capacity_factor_selection_layer,world_atlas_selection_data)
        print("Overriding Atlite with world atlas capacity factor data")
    else:
        world_atlas_selection_data = None

    # user selection:
    tiers_areas = user_area_selection(capacity_factor_selection_layer, world_atlas_selection_data)

    return tiers_areas




# Function to generate random data
def generate_random_data(latitudes, longitudes):
    maximum_capacity = 50 # MW
    return np.random.rand(len(latitudes), len(longitudes)),maximum_capacity

def create_dataset(start_date, end_date, latitudes, longitudes,**kwargs):
    # Step 1: Create hourly date times in a Pandas series
    hourly_date_times = pd.date_range(start=start_date, end=end_date, freq='H')


    """ temporary fix start """
    # Step 2: Create equally spaced intervals of 0.1 degrees between latitudes and longitudes
    latitude_intervals = np.arange(latitudes[0], latitudes[1], 0.1)
    longitude_intervals = np.arange(longitudes[0], longitudes[1], 0.1)

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
        # print("At timestep: ",i)
        #### Step 1:
        # TODO: Link to Nicolene's algorithm here
        """ temporary fix """
        capacity_factors, maximum_capacity = generate_random_data(latitude_intervals, longitude_intervals)
        atlite_capacity_factors['capacity_factors'][i, :, :] = capacity_factors
        """ temporary fix """

    print(atlite_capacity_factors["capacity_factors"].data.shape)
    print(atlite_capacity_factors["capacity_factors"])

    # resolve the world atlas if any
    if "world_atlas_capacity_factor_file" in kwargs:
        world_atlas_capacity_factor_file = kwargs["world_atlas_capacity_factor_file"]
    else:
        world_atlas_capacity_factor_file = None

    # determine user areas for tiers
    user_areas = create_capacity_factor_selection_creteria(atlite_capacity_factors,maximum_capacity,world_atlas_capacity_factor_file)
    print(user_areas)

    # TODO: use the tier areas to determine the tiers
    # ...
    return


if __name__ == "__main__":
    """user inputs here"""
    # generic user input
    start_date = '2023-01-01'
    end_date = '2024-01-01'
    bounding_box = {
        'latitudes': (-40.0, -30.0),
        'longitudes': (20.0, 30.0)
    }

    # world atlas capacity factor (optional)
    world_atlas_capacity_factor_file = "capacity_factors_world_atlas/ZAF_capacity-factor_IEC1.tif"
    create_dataset(start_date, end_date, bounding_box['latitudes'], bounding_box['longitudes'],world_atlas_capacity_factor_file=world_atlas_capacity_factor_file)




""" old codes """

"""
# #### Option 1: maximum capacities
# def create_capacity_factor_tiers_maximum(capacity_factor_data,max_capacity,number_tiers=4,index_layer=None,average=False):
#     if average:
#         capacity_factor_selection_layer = capacity_factor_data["capacity_factors"].mean(dim='time')
#     elif index_layer is not None:
#         capacity_factor_selection_layer = capacity_factor_data["capacity_factors"][index_layer]
#     else:
#         capacity_factor_selection_layer = capacity_factor_data["capacity_factors"][0]
#
#     # Convert the xarray DataArray to a numpy array
#     numpy_array = capacity_factor_selection_layer.values
#
#     # Find the indices of the number of tiers
#     flat_indices = np.argpartition(numpy_array.flatten(), -number_tiers)[-number_tiers:]
#
#     # Convert the flat indices to 2D indices (row, col)
#     indices_2d = np.unravel_index(flat_indices, numpy_array.shape)
#
#     # The 'indices_2d' variable now contains the row and column indices of the top 5 maximum values
#     # print(indices_2d[0],indices_2d[1])
#     # print(indices_2d)
#     # for index in indices_2d:
#     #     print(index)
#     #     print(capacity_factor_data['capacity_factors'][:, index[0], index[1]].values)
#
#     # Extract values for each index and create a list of time series
#     time_series_list = [capacity_factor_data['capacity_factors'][:, indices_2d[0][index], indices_2d[1][index]].values for index in range(number_tiers)]
#
#     # Create a DataFrame with columns 'tier_1', 'tier_2', etc.
#     data = {f'tier_{i + 1}': time_series for i, time_series in enumerate(time_series_list)}
#     tiers = pd.DataFrame(data)
#
#     # print(tiers)
#     return tiers/max_capacity

#### Option 2: point and surrounding capacities
def create_capacity_factor_tiers_point(capacity_factor_data,max_capacity,data_point):
    # get closest index to lats and lons and then get the points around it
    # print(capacity_factor_data["latitude"].values)
    # print(data_point[0],type(data_point[0]))

    lat_index = np.argmin(np.abs(capacity_factor_data["latitude"].values - data_point[0]))
    lon_index = np.argmin(np.abs(capacity_factor_data["longitude"].values - data_point[1]))
    # print(capacity_factor_data["latitude"].values[lat_index])
    # print(capacity_factor_data["longitude"].values[lon_index])

    # now get the timeseries around the point
    # create shell to hold indexes
    latitudes = []
    longitudes = []

    # 1. add the central point
    latitudes.append(lat_index)
    longitudes.append(lon_index)

    # 2. point above centre
    try:
        capacity_factor_data["latitude"].values[lat_index+1]
        capacity_factor_data["longitude"].values[lon_index]

        # successful, add the point
        latitudes.append(lat_index+1)
        longitudes.append(lon_index)
    except Exception as e:
        pass
    # 3. point below centre
    try:
        capacity_factor_data["latitude"].values[lat_index-1]
        capacity_factor_data["longitude"].values[lon_index]

        # successful, add the point
        latitudes.append(lat_index-1)
        longitudes.append(lon_index)
    except Exception as e:
        pass
    # 4. point left centre
    try:
        capacity_factor_data["latitude"].values[lat_index]
        capacity_factor_data["longitude"].values[lon_index-1]

        # successful, add the point
        latitudes.append(lat_index)
        longitudes.append(lon_index-1)
    except Exception as e:
        pass
    # 5. point right centre
    try:
        capacity_factor_data["latitude"].values[lat_index]
        capacity_factor_data["longitude"].values[lon_index+1]

        # successful, add the point
        latitudes.append(lat_index)
        longitudes.append(lon_index+1)
    except Exception as e:
        pass

    # Extract values for each index and create a list of time series
    time_series_list = [capacity_factor_data['capacity_factors'][:, latitudes[index], longitudes[index]].values for index in range(len(latitudes))]

    # Create a DataFrame with columns 'tier_1', 'tier_2', etc.
    data = {f'tier_{i + 1}': time_series for i, time_series in enumerate(time_series_list)}
    tiers = pd.DataFrame(data)

    # print(tiers)
    return tiers/max_capacity

#### Option 3: bin the capacities
def create_capacity_factor_tiers_bins(capacity_factor_data,max_capacity,bins,index_layer=None,average=False):
    if average:
        capacity_factor_selection_layer = capacity_factor_data["capacity_factors"].mean(dim='time')
    elif index_layer is not None:
        capacity_factor_selection_layer = capacity_factor_data["capacity_factors"][index_layer]
    else:
        capacity_factor_selection_layer = capacity_factor_data["capacity_factors"][0]

    # # Step 2: Find indexes of values between bins
    tiers = pd.DataFrame()
    for index,bin in enumerate(bins):
        print("Tiering for bin: ",bin)
        # create mask condition from bin
        conditions = (capacity_factor_selection_layer.values > bin[0]) & (capacity_factor_selection_layer.values < bin[1])
        # print(conditions)

        # create mask:
        # Extend the dimensions of the mask to match the shape of the 3D array
        extended_mask = np.broadcast_to(~conditions, capacity_factor_data['capacity_factors'].values.shape)

        # Apply the mask to the 3D array
        masked_array_3d = np.ma.masked_array(capacity_factor_data['capacity_factors'].values, extended_mask)
        # print(masked_array_3d)

        # Perform operations on the masked array
        # For example, calculate the mean of the masked array
        means = np.mean(masked_array_3d, axis=(1, 2))
        # print(mean_value)
        # print(mean_value.shape)

        # add to tier
        tiers["tier_"+str(index+1)] = means
    return tiers/max_capacity

# #### Option 4: Top certain percentage, default top 5%
# def create_capacity_factor_tiers_upper_percent(capacity_factor_data, max_capacity, upper_percentage=5, index_layer=None, average=False):
#     # takes the upper percentage of entries and then calculates the tiers
#     if average:
#         capacity_factor_selection_layer = capacity_factor_data["capacity_factors"].mean(dim='time')
#     elif index_layer is not None:
#         capacity_factor_selection_layer = capacity_factor_data["capacity_factors"][index_layer]
#     else:
#         capacity_factor_selection_layer = capacity_factor_data["capacity_factors"][0]
#
#
#
#     pass


#### Option 5: bounding box selection
def create_subset_bounding_box(capacity_factor_data,bounding_box):
    # Select the data within the bounding box in format [[min_lat,max_lat],[min_lon,max_lon]]
    lat_max = bounding_box[0][0]
    lat_min = bounding_box[0][1]
    lon_min = bounding_box[1][0]
    lon_max = bounding_box[1][1]
    subset = capacity_factor_data.sel(latitude=slice(lat_max, lat_min), longitude=slice(lon_min, lon_max))
    return subset




# Function to generate random data
def generate_random_data(latitudes, longitudes):
    maximum_capacity = 50 # MW
    return np.random.rand(len(latitudes), len(longitudes)),maximum_capacity

def create_dataset(start_date, end_date, latitudes, longitudes,**kwargs):


    # Step 1: Create hourly date times in a Pandas series
    hourly_date_times = pd.date_range(start=start_date, end=end_date, freq='H')

    # Step 2: Create equally spaced intervals of 0.1 degrees between latitudes and longitudes
    latitude_intervals = np.arange(latitudes[0], latitudes[1], 0.1)
    longitude_intervals = np.arange(longitudes[0], longitudes[1], 0.1)


    # Step 3: Create an empty Xarray dataset
    ds = xr.Dataset(
        {
            'capacity_factors': (['time', 'latitude', 'longitude'], np.zeros((len(hourly_date_times), len(latitude_intervals), len(longitude_intervals))))
        },
        coords={
            'time': hourly_date_times,
            'latitude': latitude_intervals,
            'longitude': longitude_intervals
        }
    )

    # Step 4: Loop through each hourly timestep and generate random data
    for i, time in enumerate(hourly_date_times):
        # print("At timestep: ",i)
        # TODO: Link to Nicolene's algorithm here
        capacity_factors, maximum_capacity = generate_random_data(latitude_intervals, longitude_intervals)
        ds['capacity_factors'][i, :, :] = capacity_factors

    print(ds["capacity_factors"].data.shape)
    print(ds["capacity_factors"])

    # Step 5: Aggregate to tiers
    # TODO: correction with max_capacity for all methods
    #### Option 1: maximum capacities
    tiers = create_capacity_factor_tiers_maximum(ds,maximum_capacity,number_tiers=10,index_layer=None,average=True)
    print(tiers)

    # #### Option 2: point and surrounding capacities
    # point = [-34.27, 25.3]
    # tiers = create_capacity_factor_tiers_point(ds,maximum_capacity,point)
    # print(tiers)

    # #### Option 3: bin the capacities
    # bins = [[0, 0.2], [0.2, 0.5], [0.5, 0.7]]
    # tiers = create_capacity_factor_tiers_bins(ds,maximum_capacity,bins,index_layer=None,average=True)
    # print(tiers)

    # #### Option 4: top certain percentage


    # #### Option 5: bounding box capacities [[min_lat,max_lat],[min_lon,max_lon]]
    # bounding_box = [[-38,-37],[25,27]]
    # subset = create_subset_bounding_box(ds,bounding_box)
    # print(subset["capacity_factors"])
    #
    # # select tiers method from option 1,2,3 or 4
    # # option 1: maximum
    # tiers = create_capacity_factor_tiers_maximum(subset,maximum_capacity)
    # # print(tiers)
    # # option 2: point
    # point = [-37.27, 26.3]
    # tiers = create_capacity_factor_tiers_point(subset,maximum_capacity,point)
    # # print(tiers)
    # option 3: bin
    # tiers = create_capacity_factor_tiers_bins(subset,maximum_capacity,bins)
    # print(tiers)
    # # option 4: top %




if __name__ == "__main__":
    # user inputs here
    start_date = '2023-01-01'
    end_date = '2024-01-01'
    bounding_box = {
        'latitudes': (-40.0, -30.0),
        'longitudes': (20.0, 30.0)
    }
    create_dataset(start_date, end_date, bounding_box['latitudes'], bounding_box['longitudes'])

"""


