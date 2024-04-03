"""
Purpose: User can select the pieces of tiers they wish for the final selection of the capacity factors.

author: kirodh boodhraj
"""
import dash
from dash import html
import folium
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import box, Point
import os
from dash import dash_table
import copy
import plotly.express as px
from dotenv import load_dotenv
import argparse

import Option_Support_Functions as support_functions

################################
# system args section
################################
# used for running the codes
def parse_arguments():
    parser = argparse.ArgumentParser(description="(Option 1) Script to calculate average capacity factors.")
    parser.add_argument('--ATLITE_CAPACITY_FACTORS_FOLDERS', default=None, required=False,help="Folders continaing hourly Atlite data files needing stitching.")
    parser.add_argument('--AVG_ATLITE_LONGITUDE_VARIABLE_NAME', default=None, required=False,help="Average ATLITE longitude variable name.")
    parser.add_argument('--AVG_ATLITE_LATITUDE_VARIABLE_NAME', default=None, required=False,help="Average ATLITE latitude variable name.")
    parser.add_argument('--AVG_ATLITE_DATA_VARIABLE_NAME', default=None, required=False,help="Average ATLITE data variable name.")
    parser.add_argument('--PERCENT_UPPER_TIER1_CAPACITY_FACTORS', default=None, required=False,help="User defined % bounds for capacuty factors for tier 1.")
    parser.add_argument('--PERCENT_UPPER_TIER2_CAPACITY_FACTORS', default=None, required=False,help="User defined % bounds for capacuty factors for tier 2.")
    parser.add_argument('--PERCENT_UPPER_TIER3_CAPACITY_FACTORS', default=None, required=False,help="User defined % bounds for capacuty factors for tier 3.")
    parser.add_argument('--PERCENT_UPPER_TIER4_CAPACITY_FACTORS', default=None, required=False,help="User defined % bounds for capacuty factors for tier 4.")
    parser.add_argument('--PERCENT_UPPER_TIER5_CAPACITY_FACTORS', default=None, required=False,help="User defined % bounds for capacuty factors for tier 5.")
    parser.add_argument('--DATA_VARIABLE_NAME', default=None, required=False, help="Data variable name.")
    parser.add_argument('--OPTION_6_USER_GEOMETRIES_GEOJSON_FILE', default=None, required=False,help="User defined geometries as output from Step 1.")
    parser.add_argument('--OPTION_6_OUTPUT_FOLDER', default=None, required=False, help="Option 6 output folder.")
    parser.add_argument('--ATLITE_DUMMY_DATA', default=None, required=False, help="Boolean to use the dummy Atlite data (True) or not.")
    parser.add_argument('--DUMMY_START_DATE', default=None, required=False, help="Start date.")
    parser.add_argument('--DUMMY_END_DATE', default=None, required=False, help="End date.")
    parser.add_argument('--DUMMY_LATITUDE_BOTTOM', default=None, required=False, help="Latitude bottom.")
    parser.add_argument('--DUMMY_LATITUDE_TOP', default=None, required=False, help="Latitude top.")
    parser.add_argument('--DUMMY_LONGITUDE_LEFT', default=None, required=False, help="Longitude left.")
    parser.add_argument('--DUMMY_LONGITUDE_RIGHT', default=None, required=False, help="Longitude right.")
    parser.add_argument('--MAXIMUM_CAPACITY', default=None, required=False, help="Maximum capacity.")
    parser.add_argument('--TIME_VARIABLE_NAME', default=None, required=False, help="Time variable name.")
    parser.add_argument('--AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION', default=None, required=False,help="Average ATLITE capacity factors file location.")
    parser.add_argument('--SCALE_CAPACITY_FACTORS', default=None, required=False, help="Scale capacity factors.")
    parser.add_argument('--OPTION_6_OUTPUT_TIERS_FILE', default=None, required=False,help="Output tiers file.")
    parser.add_argument('--OPTION_6_GEOMETRY_REFERENCE_FILE', default=None, required=False,help="Output geometry reference file.")
    parser.add_argument('--OPTION_6_VIEW_VALID_GEOMETRIES', default=None, required=False,help="View geometryTrue or not False.")

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
        "ATLITE_CAPACITY_FACTORS_FOLDERS" : os.environ.get("ATLITE_CAPACITY_FACTORS_FOLDERS"),
        "AVG_ATLITE_LONGITUDE_VARIABLE_NAME" : os.environ.get("AVG_ATLITE_LONGITUDE_VARIABLE_NAME"),
        "AVG_ATLITE_LATITUDE_VARIABLE_NAME" : os.environ.get("AVG_ATLITE_LATITUDE_VARIABLE_NAME"),
        "AVG_ATLITE_DATA_VARIABLE_NAME" : os.environ.get("AVG_ATLITE_DATA_VARIABLE_NAME"),
        "PERCENT_UPPER_TIER1_CAPACITY_FACTORS" : os.environ.get("PERCENT_UPPER_TIER1_CAPACITY_FACTORS"),
        "PERCENT_UPPER_TIER2_CAPACITY_FACTORS" : os.environ.get("PERCENT_UPPER_TIER2_CAPACITY_FACTORS"),
        "PERCENT_UPPER_TIER3_CAPACITY_FACTORS" : os.environ.get("PERCENT_UPPER_TIER3_CAPACITY_FACTORS"),
        "PERCENT_UPPER_TIER4_CAPACITY_FACTORS" : os.environ.get("PERCENT_UPPER_TIER4_CAPACITY_FACTORS"),
        "PERCENT_UPPER_TIER5_CAPACITY_FACTORS" : os.environ.get("PERCENT_UPPER_TIER5_CAPACITY_FACTORS"),
        "DATA_VARIABLE_NAME" : os.environ.get("DATA_VARIABLE_NAME"),
        "OPTION_6_USER_GEOMETRIES_GEOJSON_FILE" : os.environ.get("OPTION_6_USER_GEOMETRIES_GEOJSON_FILE"),
        "OPTION_6_OUTPUT_FOLDER" : os.environ.get("OPTION_6_OUTPUT_FOLDER"),
        "ATLITE_DUMMY_DATA" : os.environ.get("ATLITE_DUMMY_DATA"),
        "DUMMY_START_DATE" : os.environ.get("DUMMY_START_DATE"),
        "DUMMY_END_DATE" : os.environ.get("DUMMY_END_DATE"),
        "DUMMY_LATITUDE_BOTTOM" : os.environ.get("DUMMY_LATITUDE_BOTTOM"),
        "DUMMY_LATITUDE_TOP" : os.environ.get("DUMMY_LATITUDE_TOP"),
        "DUMMY_LONGITUDE_LEFT" : os.environ.get("DUMMY_LONGITUDE_LEFT"),
        "DUMMY_LONGITUDE_RIGHT" : os.environ.get("DUMMY_LONGITUDE_RIGHT"),
        "MAXIMUM_CAPACITY" : os.environ.get("MAXIMUM_CAPACITY"),
        "TIME_VARIABLE_NAME" : os.environ.get("TIME_VARIABLE_NAME"),
        "AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION" : os.environ.get("AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION"),
        "SCALE_CAPACITY_FACTORS" : os.environ.get("SCALE_CAPACITY_FACTORS"),
        "OPTION_6_OUTPUT_TIERS_FILE" : os.environ.get("OPTION_6_OUTPUT_TIERS_FILE"),
        "OPTION_6_GEOMETRY_REFERENCE_FILE" : os.environ.get("OPTION_6_GEOMETRY_REFERENCE_FILE"),
        "OPTION_6_VIEW_VALID_GEOMETRIES" : os.environ.get("OPTION_6_VIEW_VALID_GEOMETRIES"),
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


########################################################################
# Helper function: Check geometries, inside or outside bounding box
########################################################################
def check_geojson_within_bounds(geojson_data, xarray_dataset, AVG_ATLITE_LONGITUDE_VARIABLE_NAME, AVG_ATLITE_LATITUDE_VARIABLE_NAME):
    """

    :param geojson_data: The geojson data with geometries
    :param xarray_dataset: Atlite dataset to determine bounding box
    :return: list of geometries within and outside bounding box
    """
    # Get the bounds of the xarray dataset
    bounds = (xarray_dataset[AVG_ATLITE_LONGITUDE_VARIABLE_NAME].min(), xarray_dataset[AVG_ATLITE_LATITUDE_VARIABLE_NAME].min(), xarray_dataset[AVG_ATLITE_LONGITUDE_VARIABLE_NAME].max(), xarray_dataset[AVG_ATLITE_LATITUDE_VARIABLE_NAME].max())
    bounding_box = box(*bounds)

    print("\n... Checking if user defined geometry is within Atlite bounding box.")

    # Initialize a list to store boolean values for each geometry
    is_within_bounds_list = []

    # Loop through each geometry in the GeoJSON file
    for geometry in geojson_data['geometry']:
        if geometry.is_empty:
            # Skip empty geometries
            is_within_bounds_list.append(False)
        elif geometry.intersects(bounding_box):
            # Check if the geometry intersects the bounding box
            if geometry.within(bounding_box):
                # Check if the entire geometry is within the bounding box
                is_within_bounds_list.append(True)
            else:
                # If any point of the geometry lies outside the bounding box, append False
                is_within_bounds_list.append(False)
        else:
            # If the geometry is entirely outside the bounding box, append False
            is_within_bounds_list.append(False)

    for index, x in enumerate(is_within_bounds_list):
        if x == True:
            print("...... Tier ",index + 1," is within bounding box.")
        else:
            print("...... Tier ",index + 1," is NOT within bounding box.")

    print("... Checking if user defined geometry is within Atlite bounding box complete.")
    print("-------------------------------------------------------------------------------\n")

    return is_within_bounds_list


#################################################
## Helper function: obtain the tiers per valid geometry
#################################################
def calculate_valid_tiers(atlite_data,atlite_data_avg,points_geometry,geometry,AVG_ATLITE_LATITUDE_VARIABLE_NAME, AVG_ATLITE_LONGITUDE_VARIABLE_NAME, AVG_ATLITE_DATA_VARIABLE_NAME, PERCENT_UPPER_TIER1_CAPACITY_FACTORS, PERCENT_UPPER_TIER2_CAPACITY_FACTORS, PERCENT_UPPER_TIER3_CAPACITY_FACTORS, PERCENT_UPPER_TIER4_CAPACITY_FACTORS, PERCENT_UPPER_TIER5_CAPACITY_FACTORS, DATA_VARIABLE_NAME):
    """

    :param atlite_data: Full Atlite data
    :param atlite_data_avg: Averaged Atlite data
    :param points_geometry: The geometry's points
    :param geometry: Type of geometry i.e. Point, LineString, Polygon etc.
    :return: Dataframe of valid tiers (Polygon) or tier (Point)
    """

    # if point, then find the closest point on the grid and use this as the tier
    if geometry == "Point":
        print("... Dealing with POINT geometry")
        # Find the nearest latitude and longitude in the xarray dataset
        lat_index = np.abs(atlite_data[AVG_ATLITE_LATITUDE_VARIABLE_NAME] - points_geometry.y).argmin().item()
        lon_index = np.abs(atlite_data[AVG_ATLITE_LONGITUDE_VARIABLE_NAME] - points_geometry.x).argmin().item()

        # # Extract the nearest latitude and longitude values
        # nearest_lat = float(atlite_data[os.environ.get("AVG_ATLITE_LATITUDE_VARIABLE_NAME")].values[lat_index])
        # nearest_lon = float(atlite_data[os.environ.get("AVG_ATLITE_LONGITUDE_VARIABLE_NAME")].values[lon_index])

        # Select the data at the nearest point
        capacity_factors_at_nearest_point = atlite_data[AVG_ATLITE_DATA_VARIABLE_NAME][:,lat_index,lon_index]
        # Create a DataFrame
        tier_dataframe_option_6_point = pd.DataFrame({
            'tier_1': capacity_factors_at_nearest_point.values,
        })

        print("... Generated tier successfully: ")
        print(tier_dataframe_option_6_point)
        print("#########################################\n")

        return tier_dataframe_option_6_point

    # else if it is a polygon, then find all coordinates within the polygon and then get tiers with the bounds
    elif geometry == "Polygon":
        print("... Dealing with POLYGON geometry")

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

        # get the geometry bound:
        geometry_bound = points_geometry.bounds

        # Select the subset of data within the bounding box
        # subset avg Atlite data
        subset = atlite_data_avg.sel(latitude=slice(geometry_bound[1], geometry_bound[3]), longitude=slice(geometry_bound[0], geometry_bound[2]))
        # subset full Atlite data
        subset_full_dataset = atlite_data.sel(latitude=slice(geometry_bound[1], geometry_bound[3]), longitude=slice(geometry_bound[0], geometry_bound[2]))

        ## Debug by plotting the geometry within the bounding box, before and after pics
        # import matplotlib.pyplot as plt
        # # Plot initial subset
        # if True:
        #     plt.figure()
        #     plt.pcolormesh(subset.longitude, subset.latitude, subset.values)
        #     plt.colorbar(label='Value')
        #     plt.title('Initial Subset')
        #     plt.xlabel('Longitude')
        #     plt.ylabel('Latitude')
        #     plt.savefig("assets/before.png")
        #     plt.close()

        # start with the masking of the values outside thw geometry in the subsetted data
        # Create meshgrid of latitude and longitude values of subset data, for getting geometry
        lon, lat = np.meshgrid(subset.longitude.values, subset.latitude.values)

        # Reshape latitude and longitude values to 1D arrays
        lat_flat = lat.flatten()
        lon_flat = lon.flatten()

        # Create points array
        points = np.column_stack((lon_flat, lat_flat))

        # Create a mask for points within the polygon
        mask = np.array([points_geometry.contains(Point(p)) for p in points])

        # Reshape mask to the shape of the subset
        mask_reshaped = mask.reshape(subset.latitude.size, subset.longitude.size)

        # Set points outside the polygon to NaN
        subset.values[~mask_reshaped] = np.nan
        # set all nan to 0, this will allow the percentiles to be computed and not come out as nan
        subset = subset.fillna(0)

        # Repeat the mask along the time dimension to match the full dataset, needed for tier extraction
        mask_time = np.repeat(mask_reshaped[np.newaxis, :, :], len(atlite_data[DATA_VARIABLE_NAME].values[:,0,0]), axis=0)

        # set points outside geometry to nan
        subset_full_dataset[DATA_VARIABLE_NAME].values[~mask_time] = np.nan
        # dont set to 0 because the code for tier generation for each percentile checks for nan specifically
        # subset_full_dataset = subset_full_dataset.fillna(0)

        # # Debugging Plot masked subset after
        # if True:
        #     plt.figure()
        #     plt.pcolormesh(subset.longitude, subset.latitude, subset.values)
        #     plt.colorbar(label='Value')
        #     plt.title('Masked Subset')
        #     plt.xlabel('Longitude')
        #     plt.ylabel('Latitude')
        #     plt.savefig("assets/after.png")
        #     plt.close()

        # Calculate percentiles for each tier based on the extracted values
        bounds_tier1 = np.percentile(subset,[lower_percentile_tier1 * 100, upper_percentile_tier1 * 100])
        bounds_tier2 = np.percentile(subset,[lower_percentile_tier2 * 100, upper_percentile_tier2 * 100])
        bounds_tier3 = np.percentile(subset,[lower_percentile_tier3 * 100, upper_percentile_tier3 * 100])
        bounds_tier4 = np.percentile(subset,[lower_percentile_tier4 * 100, upper_percentile_tier4 * 100])
        bounds_tier5 = np.percentile(subset,[lower_percentile_tier5 * 100, upper_percentile_tier5 * 100])

        print("... Bounds for this geometry:")
        print("...... Bounds for tier 1:", bounds_tier1)
        print("...... Bounds for tier 2:", bounds_tier2)
        print("...... Bounds for tier 3:", bounds_tier3)
        print("...... Bounds for tier 4:", bounds_tier4)
        print("...... Bounds for tier 5:", bounds_tier5)

        # extract the bounds:
        top_bound_tier1 = bounds_tier1[1]
        top_bound_tier2 = bounds_tier2[1]
        top_bound_tier3 = bounds_tier3[1]
        top_bound_tier4 = bounds_tier4[1]
        top_bound_tier5 = bounds_tier5[1]

        bottom_bound_tier1 = bounds_tier1[0]
        bottom_bound_tier2 = bounds_tier2[0]
        bottom_bound_tier3 = bounds_tier3[0]
        bottom_bound_tier4 = bounds_tier4[0]
        bottom_bound_tier5 = bounds_tier5[0]

        # Use boolean indexing to select the desired indexes from subset
        selected_indexes_tier1 = subset.where((subset > bottom_bound_tier1) & (subset < top_bound_tier1))
        selected_indexes_tier2 = subset.where((subset > bottom_bound_tier2) & (subset < top_bound_tier2))
        selected_indexes_tier3 = subset.where((subset > bottom_bound_tier3) & (subset < top_bound_tier3))
        selected_indexes_tier4 = subset.where((subset > bottom_bound_tier4) & (subset < top_bound_tier4))
        selected_indexes_tier5 = subset.where((subset > bottom_bound_tier5) & (subset < top_bound_tier5))

        # Generate the tiers:
        bound_tier1 = get_tier_percentage_bound(subset[AVG_ATLITE_LATITUDE_VARIABLE_NAME].values,subset[AVG_ATLITE_LONGITUDE_VARIABLE_NAME].values,copy.deepcopy(subset_full_dataset), selected_indexes_tier1,DATA_VARIABLE_NAME)
        bound_tier2 = get_tier_percentage_bound(subset[AVG_ATLITE_LATITUDE_VARIABLE_NAME].values,subset[AVG_ATLITE_LONGITUDE_VARIABLE_NAME].values,copy.deepcopy(subset_full_dataset), selected_indexes_tier2,DATA_VARIABLE_NAME)
        bound_tier3 = get_tier_percentage_bound(subset[AVG_ATLITE_LATITUDE_VARIABLE_NAME].values,subset[AVG_ATLITE_LONGITUDE_VARIABLE_NAME].values,copy.deepcopy(subset_full_dataset), selected_indexes_tier3,DATA_VARIABLE_NAME)
        bound_tier4 = get_tier_percentage_bound(subset[AVG_ATLITE_LATITUDE_VARIABLE_NAME].values,subset[AVG_ATLITE_LONGITUDE_VARIABLE_NAME].values,copy.deepcopy(subset_full_dataset), selected_indexes_tier4,DATA_VARIABLE_NAME)
        bound_tier5 = get_tier_percentage_bound(subset[AVG_ATLITE_LATITUDE_VARIABLE_NAME].values,subset[AVG_ATLITE_LONGITUDE_VARIABLE_NAME].values,copy.deepcopy(subset_full_dataset), selected_indexes_tier5,DATA_VARIABLE_NAME)

        # Create a DataFrame
        tier_dataframe_option_6 = pd.DataFrame({
            'tier_1': bound_tier1,
            'tier_2': bound_tier2,
            'tier_3': bound_tier3,
            'tier_4': bound_tier4,
            'tier_5': bound_tier5
        })
        print("... Generated tiers successfully: ")
        print(tier_dataframe_option_6)
        print("#########################################\n")

        return tier_dataframe_option_6

    # else return nothing
    else:
        print("... No tier generated! You provided a geometry of type: ",geometry)
        print("#########################################\n")
        return None



#################################################
## Helper function: visualize geometries
#################################################
# dash app
def visualize_geometries(geographical_bounds_atlite_data,geometry_table_list,geometry_layer_list,graph_tier_list):
    # create app
    app = dash.Dash(__name__)

    ### dash layout elemets

    ################################
    # MAP
    ################################
    m = folium.Map(location=[-30.5595, 22.9375], zoom_start=5,height="100%")

    # Atlite geographical bounds as rectangle polygon
    user_bound_frame = folium.Rectangle(
        bounds=geographical_bounds_atlite_data,
        color='blue',
        fill=False,
        weight=5,
        opacity=1.0,
        popup=folium.Popup('Valid points and polygons lie within this bounding box!', parse_html=True),  # Add a message to the rectangle
    )
    user_bound_frame.add_to(m)

    # add geometries to the map:
    for geometry_layer in geometry_layer_list:
        geometry_layer.add_to(m)

    #######################################
    ## Header, footer, spacing
    #######################################

    # HEADER
    main_header = html.Div(
        [
            html.H1("Single tier per geometry option 6 (Step 2 of 2)", style={'textAlign': 'center', 'color': 'white', 'background-color': 'lightgreen', 'padding': '20px'}),
            html.Ul([
                html.Li("1. Please find your geometries classified here (polygons and points, inside or outside the bounding box)."),
                html.Li("2. Please take note of the tier number assigned to your geometry."),
                html.Li("3. Note that line geometry are not used."),
                html.Li("4. The geometries within the bounding box will be green and are valid tiers. Geometries outside the bounding box arecoloured red and are discarded and no tier will be created for this geometry."),
                html.Li("5. Thank you for using these codes.")
            ], style={'list-style-type': 'none', 'margin': '30px','background-color': 'lightblue', 'padding': '30px'}),
        ],
        style={'margin-top': '20px', 'margin-bottom': '20px'}
    )

    # FOOTER
    footer = html.Div(
        [
            html.Img(src=app.get_asset_url('static/csir_logo.jpg'), style={'width': '150px', 'height': 'auto', 'margin-right': '20px'}),
            html.Img(src=app.get_asset_url('static/leapre_logo.jpg'), style={'width': '150px', 'height': 'auto', 'margin-left': '20px'}),
        ],
        style={'bottom': 0, 'width': '95vw', 'padding': '20px', 'background-color': 'lightgray', 'text-align': 'center'}
    )

    # SPACING
    spacing = html.Div(style={'bottom': 0, 'width': '90%', 'padding': '20px', 'background-color': 'white', 'text-align': 'center'})


    #######################################
    ## First section
    #######################################

    # Table layout
    table_layout = html.Div([
        dash_table.DataTable(
            id='table',
            columns=[
                {'name': 'Tier', 'id': 'Tier'},
                {'name': 'Geometry Type', 'id': 'Geometry Type'},
                {'name': 'Coordinates', 'id': 'Coordinates'},
                {'name': 'Result', 'id': 'Result'},
            ],
            data=geometry_table_list,
            style_table={'width': '80%', 'margin': '0 auto'},
            style_cell={'textAlign': 'center'},
            style_data_conditional=[
                {
                    'if': {'column_id': 'Result'},
                    'color': 'green',
                },
                {
                    'if': {'column_id': 'Result', 'filter_query': '{Result} eq "Outside, Invalid"'},
                    'color': 'red',
                },
                {
                    'if': {'column_id': 'Coordinates'},
                    'whiteSpace': 'normal',
                    'height': 'auto',
                },
            ],
        ),
    ],style={'textAlign': 'center'},)

    # Folium map layout
    map_layout = html.Div([
        html.Iframe(id='map', srcDoc=m._repr_html_(), width='70%', height='650', style={'margin': '0 auto'})
    ],style={'textAlign': 'center'},)

    #######################################
    ## Graphing of tiers
    #######################################
    # # check if the valid tiers is an empty dataframe:
    # if dataframe.empty:
    #     print("... WARNING EMPTY TIERS FILE, CHECK IF ANY GEOMETRIES AE WITHIN THE BOUNDING BOX")
    #     # fill with empty df:
    #     # Create an example DataFrame
    #     data = {
    #         'Tier 1': [0, 0, 0],
    #         'Tier 2': [0, 0, 0],
    #         'Tier 3': [0, 0, 0]
    #     }
    #     index = ['Metric 1', 'Metric 2', 'Metric 3']
    #     dataframe = pd.DataFrame(data, index=index)


    graphs = html.Div(id='graph-container', children=[
        html.H1("Tier Graphs",style={'textAlign': 'center',}),
        html.Div(id='graphs', children=[
            html.Div([
                dash.dcc.Graph(figure=px.line(dataframe, x=dataframe.index, y=dataframe.columns, title=f'Tier: {tier_label}',labels={'index': 'Time Steps', 'value': 'Capacity Factor'})) for entry in graph_tier_list for tier_label, dataframe in entry.items()
            ])
        ])
    ])


    #######################################
    ## Pull all layout elements together
    #######################################

    # App layout
    app.layout = html.Div([
        # geometry validation
        main_header,
        table_layout,
        spacing,
        spacing,
        map_layout,
        spacing,
        graphs,
        spacing,
        footer,
    ])

    app.run_server(debug=True)

################################################################
# Helper function: Split tiers according to percentage bounds:
################################################################
def get_tier_percentage_bound(lats,longs,atlite_data,selected_data,DATA_VARIABLE_NAME):
    """

    :param lats: list of latitudes
    :param longs: list of longitudes
    :param atlite_data: full Atlite data
    :param selected_data: masked array with geometry
    :return: final averaged tier for the bounded percentile
    """
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

#################################################
## Option 6: main function to process geometries
#################################################

def option_6_process_geometries_into_tiers(ATLITE_CAPACITY_FACTORS_FOLDERS, AVG_ATLITE_LONGITUDE_VARIABLE_NAME, AVG_ATLITE_LATITUDE_VARIABLE_NAME, AVG_ATLITE_DATA_VARIABLE_NAME, PERCENT_UPPER_TIER1_CAPACITY_FACTORS, PERCENT_UPPER_TIER2_CAPACITY_FACTORS, PERCENT_UPPER_TIER3_CAPACITY_FACTORS, PERCENT_UPPER_TIER4_CAPACITY_FACTORS, PERCENT_UPPER_TIER5_CAPACITY_FACTORS, DATA_VARIABLE_NAME, OPTION_6_USER_GEOMETRIES_GEOJSON_FILE, OPTION_6_OUTPUT_FOLDER, ATLITE_DUMMY_DATA, DUMMY_START_DATE, DUMMY_END_DATE, DUMMY_LATITUDE_BOTTOM, DUMMY_LATITUDE_TOP, DUMMY_LONGITUDE_LEFT, DUMMY_LONGITUDE_RIGHT, MAXIMUM_CAPACITY, TIME_VARIABLE_NAME, AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION, SCALE_CAPACITY_FACTORS, OPTION_6_OUTPUT_TIERS_FILE, OPTION_6_GEOMETRY_REFERENCE_FILE, OPTION_6_VIEW_VALID_GEOMETRIES):
    """
    Main function for the processing of geometries into tiers

    :return: saves the tiers and geometry information
    """

    # Define the path to the GeoJSON file
    geojson_path = OPTION_6_USER_GEOMETRIES_GEOJSON_FILE

    # open the file
    try:
        geojson_data = gpd.read_file(geojson_path)
        print("... Read in geometry file successfully.\n")
    except Exception as e:
        raise ValueError("Could not read the geometry geojson file. Please check the file name and geometry content. Full error: " + str(e))

    # check if output directories are created
    if not os.path.exists(OPTION_6_OUTPUT_FOLDER):
        os.makedirs(OPTION_6_OUTPUT_FOLDER)

    ########################################################################
    ## open atlite capacity factor data
    ########################################################################
    # open the averaged atlite capacity factor data
    atlite_capacity_factors, atlite_capacity_factors_avg = support_functions.create_average_capacity_factor_file_atlite(ATLITE_CAPACITY_FACTORS_FOLDERS, ATLITE_DUMMY_DATA,DUMMY_START_DATE,DUMMY_END_DATE,DUMMY_LATITUDE_BOTTOM,DUMMY_LATITUDE_TOP,DUMMY_LONGITUDE_LEFT,DUMMY_LONGITUDE_RIGHT,MAXIMUM_CAPACITY,DATA_VARIABLE_NAME,TIME_VARIABLE_NAME,AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION)
    print("... Read averaged atlite capacity factor data.\n")

    # Call the function to check if each geometry is within the bounds
    inside_or_outside = check_geojson_within_bounds(geojson_data, atlite_capacity_factors, AVG_ATLITE_LONGITUDE_VARIABLE_NAME, AVG_ATLITE_LATITUDE_VARIABLE_NAME)

    # Initialize a list to store visualization table data
    geometry_table_list = []

    # Initialize a list to store geometry layer data
    geometry_layer_list = []

    # Graph tier list i.e. all tiers per geometry in df stored in this list
    graph_tier_list = []

    ########################################################################
    ## Bounding box
    ########################################################################
    # add the bounding box user should stay within
    # Get the maximum and minimum latitude and longitude values
    max_latitude = atlite_capacity_factors[AVG_ATLITE_LATITUDE_VARIABLE_NAME].max().values
    min_latitude = atlite_capacity_factors[AVG_ATLITE_LATITUDE_VARIABLE_NAME].min().values
    max_longitude = atlite_capacity_factors[AVG_ATLITE_LONGITUDE_VARIABLE_NAME].max().values
    min_longitude = atlite_capacity_factors[AVG_ATLITE_LONGITUDE_VARIABLE_NAME].min().values

    # Loop through each geometry in the GeoJSON file
    # add table entry and geometry on map and create tiers data
    print("... Looping through geometries.")
    for index, row in geojson_data.iterrows():
        # read geometry and metadata
        geometry_type = row['geometry'].geom_type
        is_within_bounds = inside_or_outside[index]
        tier_label = f'tier_{index + 1}'

        # Add geometry to the Folium map with styling based on conditions
        ## POLYGON:
        if geometry_type == 'Polygon':
            # this is for the map
            geometry_layer_list.append(folium.Polygon(
                locations=[x[::-1] for x in list(row['geometry'].exterior.coords)], # swap the lon/lat, or else wrong place on world
                color='green' if is_within_bounds else 'red',
                fill=True,
                fill_color='green' if is_within_bounds else 'red',
                fill_opacity=0.5,
                dash_array='dashed' if not is_within_bounds else 'solid',
                popup=tier_label  # Add popup with tier label
            ))

            # this is for the table
            # Populate the table data for each geometry
            geometry_table_list.append({
                'Tier': tier_label,
                'Geometry Type': geometry_type,
                'Coordinates': str(row['geometry']),
                'Result': 'Inside, Valid' if is_within_bounds else 'Outside, Invalid',
            })

            # generate tier data if inside the bounding box
            if is_within_bounds:
                print("------------------------------------------------")
                print(tier_label," is a POLYGON")
                potential_tier = calculate_valid_tiers(atlite_capacity_factors,atlite_capacity_factors_avg,row['geometry'],geometry_type,AVG_ATLITE_LATITUDE_VARIABLE_NAME, AVG_ATLITE_LONGITUDE_VARIABLE_NAME, AVG_ATLITE_DATA_VARIABLE_NAME, PERCENT_UPPER_TIER1_CAPACITY_FACTORS, PERCENT_UPPER_TIER2_CAPACITY_FACTORS, PERCENT_UPPER_TIER3_CAPACITY_FACTORS, PERCENT_UPPER_TIER4_CAPACITY_FACTORS, PERCENT_UPPER_TIER5_CAPACITY_FACTORS, DATA_VARIABLE_NAME)
                if potential_tier is not None:
                    print("... Tier generated successfully for ",tier_label)
                    graph_tier_list.append({tier_label:potential_tier})

                    # format the tier data for the tier piece selection
                    valid_output_tiers = potential_tier
                    print("\n... Finished compiling tier: ",tier_label,": successfully:")

                    # scale capacity factors if required:
                    if SCALE_CAPACITY_FACTORS.lower() == "true":
                        valid_output_tiers = valid_output_tiers / float(MAXIMUM_CAPACITY)  # divide by the weightings
                        print("\n... Capacity factors were scaled by division of maximum capacity:",MAXIMUM_CAPACITY)

                    # Save tiers to csv file
                    valid_output_tiers.to_csv(os.path.join(OPTION_6_OUTPUT_FOLDER,str(tier_label)+"_"+OPTION_6_OUTPUT_TIERS_FILE))
                    print("\n... Saved output tiers file to:", os.path.join(OPTION_6_OUTPUT_FOLDER,str(tier_label)+"_"+OPTION_6_OUTPUT_TIERS_FILE))

                    # otherwise, no tier for this point
                else:
                    print("... No tier for ",tier_label)

        elif geometry_type == 'LineString':
            geometry_layer_list.append(folium.PolyLine(
                locations=[x[::-1] for x in list(row['geometry'].coords)],
                color='red',
                dash_array='dashed',
                popup=tier_label  # Add popup with tier label
            ))

            # Populate the table data for each geometry
            geometry_table_list.append({
                'Tier': tier_label,
                'Geometry Type': geometry_type,
                'Coordinates': str(row['geometry']),
                'Result': 'Outside, Invalid',
            })

            # no tiers for line strings
            print("... No tier for LINE STRINGS: ", tier_label)

        elif geometry_type == 'Point':
            # for the map
            geometry_layer_list.append(folium.CircleMarker(
                location=list(row['geometry'].coords)[0][::-1],
                radius=5,
                color='green' if is_within_bounds else 'red',
                fill=True,
                fill_color='green' if is_within_bounds else 'red',
                dash_array='dashed' if not is_within_bounds else 'solid',
                popup=tier_label  # Add popup with tier label
            ))

            # Populate the table data for each geometry
            geometry_table_list.append({
                'Tier': tier_label,
                'Geometry Type': geometry_type,
                'Coordinates': str(row['geometry']),
                'Result': 'Inside, Valid' if is_within_bounds else 'Outside, Invalid',
            })

            # generate tier data
            if is_within_bounds:
                print("------------------------------------------------")
                print(tier_label," is a POINT")
                potential_tier = calculate_valid_tiers(atlite_capacity_factors,atlite_capacity_factors_avg, row['geometry'], geometry_type,AVG_ATLITE_LATITUDE_VARIABLE_NAME, AVG_ATLITE_LONGITUDE_VARIABLE_NAME, AVG_ATLITE_DATA_VARIABLE_NAME, PERCENT_UPPER_TIER1_CAPACITY_FACTORS, PERCENT_UPPER_TIER2_CAPACITY_FACTORS, PERCENT_UPPER_TIER3_CAPACITY_FACTORS, PERCENT_UPPER_TIER4_CAPACITY_FACTORS, PERCENT_UPPER_TIER5_CAPACITY_FACTORS, DATA_VARIABLE_NAME)
                if potential_tier is not None:
                    print("... Tier generated successfully for ",tier_label)
                    graph_tier_list.append({tier_label:potential_tier})

                    # format the tier data for the tier piece selection
                    valid_output_tiers = potential_tier
                    print("\n... Finished compiling tier: ",tier_label,": successfully:")

                    # scale capacity factors if required:
                    if SCALE_CAPACITY_FACTORS.lower() == "true":
                        valid_output_tiers = valid_output_tiers / float(MAXIMUM_CAPACITY)  # divide by the weightings
                        print("\n... Capacity factors were scaled by division of maximum capacity:",MAXIMUM_CAPACITY)


                    # Save tiers to csv file
                    valid_output_tiers.to_csv(os.path.join(OPTION_6_OUTPUT_FOLDER,str(tier_label)+"_"+OPTION_6_OUTPUT_TIERS_FILE))
                    print("... Saved output tiers file to:", os.path.join(OPTION_6_OUTPUT_FOLDER,str(tier_label)+"_"+OPTION_6_OUTPUT_TIERS_FILE))

                    # otherwise, no tier for this point
                else:
                    print("... No tier for ", tier_label)
        else:
            # unknown geometry type
            print("... ",geometry_type," is not supported. Only POLYGON, or POINTS allowed.")

    # Save valid geometries to file:
    # Convert the list of dictionaries to a pandas DataFrame
    geometry_table_df = pd.DataFrame(geometry_table_list)

    # Save the DataFrame to a CSV file
    geometry_table_df.to_csv(os.path.join(OPTION_6_OUTPUT_FOLDER,OPTION_6_GEOMETRY_REFERENCE_FILE))


    print("\n... Saved output reference geometry file to:",os.path.join(OPTION_6_OUTPUT_FOLDER,OPTION_6_GEOMETRY_REFERENCE_FILE))
    print("... Tier generation completed successfully!")
    print("\nOption_6 completed successfully!")
    print("----------------------------------------------------------------\n")



    if OPTION_6_VIEW_VALID_GEOMETRIES.lower() == "true":
        print("\nVisualization starting up ...")
        # build the Atlite bounding box:
        geographical_bounds_atlite_data = [[min_latitude, min_longitude], [max_latitude, max_longitude]]
        #visualize with Dash
        visualize_geometries(geographical_bounds_atlite_data,geometry_table_list,geometry_layer_list,graph_tier_list)
    else:
        print("\nNo visualization selected. If you want to visualize thedata set the OPTION_6_VIEW_VALID_GEOMETRIES to true.")

if __name__ == '__main__':
    print("Starting tier processing for Option 6: multiple tier per user defined geometry ...")
    # check args or load env file and run codes
    try:
        print("TRYING TO USE ARGUMENTS")
        args = parse_arguments()
        print("ARGUMENTS FOUND. USING ARGUMENTS")

        # RUN CODES
        option_6_process_geometries_into_tiers(**vars(args))
    except Exception as e:
        print("ARGUMENTS NOT FOUND: ", e)
        try:
            print("TRYING TO LOAD ENV FILE VARIABLES")
            # Load variables from the .env file
            args = load_from_env()
            print("ENV FILE FOUND. USING ENV FILE")

            # RUN CODES
            option_6_process_geometries_into_tiers(**args)

        except Exception as e:
            print("ENV FILE NOT FOUND: ", e)
            print("ERROR ... USER ARGS AND ENV FILE NOT FOUND, ABORTING!")
            raise ValueError("COULD NOT FIND ARGS OR LOAD ENV FILE. USER ARGS OR ENV FILE MISSING.")

    # args example use:
    # python Option_6_step2_tier_generation_bounds_per_geometry.py --AVG_ATLITE_LONGITUDE_VARIABLE_NAME longitude --AVG_ATLITE_LATITUDE_VARIABLE_NAME latitude --AVG_ATLITE_DATA_VARIABLE_NAME capacity_factors --PERCENT_UPPER_TIER1_CAPACITY_FACTORS  0,10 --PERCENT_UPPER_TIER2_CAPACITY_FACTORS  10,20 --PERCENT_UPPER_TIER3_CAPACITY_FACTORS  0,40 --PERCENT_UPPER_TIER4_CAPACITY_FACTORS  60,100 --PERCENT_UPPER_TIER5_CAPACITY_FACTORS 40,60 --DATA_VARIABLE_NAME capacity_factors --OPTION_6_USER_GEOMETRIES_GEOJSON_FILE  "assets/user_geometry/example2.geojson" --OPTION_6_OUTPUT_FOLDER "assets/option_6_output"  --ATLITE_DUMMY_DATA True  --DUMMY_START_DATE  '2023-01-01' --DUMMY_END_DATE '2024-01-01'  --DUMMY_LATITUDE_BOTTOM  -32 --DUMMY_LATITUDE_TOP -30  --DUMMY_LONGITUDE_LEFT 26  --DUMMY_LONGITUDE_RIGHT 28   --MAXIMUM_CAPACITY  50  --TIME_VARIABLE_NAME  time --AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION "assets/avg_atlite_capacity_factors.nc" --SCALE_CAPACITY_FACTORS True --OPTION_6_OUTPUT_TIERS_FILE  "option_6_multiple_tiers_per_geometry.csv" --OPTION_6_GEOMETRY_REFERENCE_FILE  "option_6_geometry_reference_file.csv"  --OPTION_6_VIEW_VALID_GEOMETRIES False


