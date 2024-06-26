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
import plotly.express as px
from dotenv import load_dotenv
import argparse

import Option_Support_Functions as support_functions

################################
# system args section
################################
# used for running the codes
def parse_arguments():
    parser = argparse.ArgumentParser(description="(Option 5 Step 2) Script to calculate average capacity factors.")
    parser.add_argument('--ATLITE_CAPACITY_FACTORS_FOLDERS', default=None, required=False,help="Folders continaing hourly Atlite data files needing stitching.")
    parser.add_argument('--AVG_ATLITE_LONGITUDE_VARIABLE_NAME', default=None, required=False,help="Average ATLITE longitude variable name.")
    parser.add_argument('--AVG_ATLITE_LATITUDE_VARIABLE_NAME', default=None, required=False,help="Average ATLITE latitude variable name.")
    parser.add_argument('--AVG_ATLITE_DATA_VARIABLE_NAME', default=None, required=False,help="Average ATLITE data variable name.")
    parser.add_argument('--OPTION_5_USER_GEOMETRIES_GEOJSON_FILE', default=None, required=False,help="User defined geometries as output from Step 1.")
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
    parser.add_argument('--OPTION_5_OUTPUT_FOLDER', default=None, required=False, help="Option 5 output folder.")
    parser.add_argument('--SCALE_CAPACITY_FACTORS', default=None, required=False, help="Scale capacity factors.")
    parser.add_argument('--OPTION_5_OUTPUT_TIERS_FILE', default=None, required=False,help="Output tiers file.")
    parser.add_argument('--OPTION_5_GEOMETRY_REFERENCE_FILE', default=None, required=False,help="Output geometry reference file.")
    parser.add_argument('--OPTION_5_VIEW_VALID_GEOMETRIES', default=None, required=False,help="View geometryTrue or not False.")

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
        "OPTION_5_USER_GEOMETRIES_GEOJSON_FILE" : os.environ.get("OPTION_5_USER_GEOMETRIES_GEOJSON_FILE"),
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
        "OPTION_5_OUTPUT_FOLDER" : os.environ.get("OPTION_5_OUTPUT_FOLDER"),
        "SCALE_CAPACITY_FACTORS" : os.environ.get("SCALE_CAPACITY_FACTORS"),
        "OPTION_5_OUTPUT_TIERS_FILE" : os.environ.get("OPTION_5_OUTPUT_TIERS_FILE"),
        "OPTION_5_GEOMETRY_REFERENCE_FILE" : os.environ.get("OPTION_5_GEOMETRY_REFERENCE_FILE"),
        "OPTION_5_VIEW_VALID_GEOMETRIES" : os.environ.get("OPTION_5_VIEW_VALID_GEOMETRIES"),
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


################################
# Helper function: Check geometries, inside or outside bounding box
################################
def check_geojson_within_bounds(geojson_data, xarray_dataset,AVG_ATLITE_LONGITUDE_VARIABLE_NAME, AVG_ATLITE_LATITUDE_VARIABLE_NAME):
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
def calculate_valid_tiers(atlite_data,points_geometry,geometry, AVG_ATLITE_LATITUDE_VARIABLE_NAME, AVG_ATLITE_LONGITUDE_VARIABLE_NAME, AVG_ATLITE_DATA_VARIABLE_NAME):
    # returns a list of numbers for the tier
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

        print("... Generated tiers successfully: ")
        print(capacity_factors_at_nearest_point)
        print("#########################################\n")

        return capacity_factors_at_nearest_point.values

    # else if it is a polygon, then find all coordinates within the polygon and then average spatially
    elif geometry == "Polygon":
        print("... Dealing with POLYGON geometry")

        # Extract lat and lon values from the xarray dataset
        lats = atlite_data[AVG_ATLITE_LATITUDE_VARIABLE_NAME].values
        lons = atlite_data[AVG_ATLITE_LONGITUDE_VARIABLE_NAME].values

        # Create a list of Point objects for each (lat, lon) pair in the dataset
        points = [Point(lon, lat) for lat, lon in zip(lats, lons)]

        # Now you can use the indices of the points within the polygon to select data from the xarray dataset
        selected_data = atlite_data.sel(latitude=[point.y for point in points],longitude=[point.x for point in points])

        # Spatially average the selected data over lat and lon dimensions
        spatially_averaged_data = selected_data.mean(dim=[AVG_ATLITE_LATITUDE_VARIABLE_NAME, AVG_ATLITE_LONGITUDE_VARIABLE_NAME], skipna=True)

        print("... Generated tiers successfully: ")
        print(spatially_averaged_data)
        print("#########################################\n")

        return spatially_averaged_data[AVG_ATLITE_DATA_VARIABLE_NAME].values

    # else return nothing
    else:
        print("... No tier generated! You provided a geometry of type: ",geometry)
        print("#########################################\n")
        return None


#################################################
## Helper function: visualize geometries
#################################################
# dash app
def visualize_geometries(geographical_bounds_atlite_data,geometry_table_list,valid_output_tiers,geometry_layer_list):
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
            html.H1("Single tier per geometry option 5 (Step 2 of 2)", style={'textAlign': 'center', 'color': 'white', 'background-color': 'lightgreen', 'padding': '20px'}),
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

    # check if the valid tiers is an empty dataframe:
    if valid_output_tiers.empty:
        print("... WARNING EMPTY TIERS FILE, CHECK IF ANY GEOMETRIES AE WITHIN THE BOUNDING BOX")
        #fill with empty df:
        # Create an example DataFrame
        data = {
            'Tier 1': [0, 0, 0],
            'Tier 2': [0, 0, 0],
            'Tier 3': [0, 0, 0]
        }
        index = ['Metric 1', 'Metric 2', 'Metric 3']
        valid_output_tiers = pd.DataFrame(data, index=index)

    graphs = html.Div(id='graph-container', children=[
        html.H1("Tier Graphs",style={'textAlign': 'center',}),
        html.Div(id='graphs', children=[
            html.Div([
                # dash.dcc.Graph(figure=px.line(dataframe, x=dataframe.index, y=dataframe.columns, title=f'Tier: {tier_label}',labels={'index': 'Time Steps', 'value': 'Capacity Factor'})) for entry in valid_output_tiers for tier_label, dataframe in entry.items()
                dash.dcc.Graph(figure=px.line(valid_output_tiers, x=valid_output_tiers.index, y=valid_output_tiers.columns, title=f'Tier graph',labels={'index': 'Time Steps', 'value': 'Capacity Factor'}))
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

#################################################
## Option 5: main function to process geometries
#################################################

def option_5_process_geometries_into_tiers(ATLITE_CAPACITY_FACTORS_FOLDERS, AVG_ATLITE_LONGITUDE_VARIABLE_NAME, AVG_ATLITE_LATITUDE_VARIABLE_NAME, AVG_ATLITE_DATA_VARIABLE_NAME, OPTION_5_USER_GEOMETRIES_GEOJSON_FILE, ATLITE_DUMMY_DATA, DUMMY_START_DATE, DUMMY_END_DATE, DUMMY_LATITUDE_BOTTOM, DUMMY_LATITUDE_TOP, DUMMY_LONGITUDE_LEFT, DUMMY_LONGITUDE_RIGHT, MAXIMUM_CAPACITY, DATA_VARIABLE_NAME, TIME_VARIABLE_NAME, AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION, OPTION_5_OUTPUT_FOLDER, SCALE_CAPACITY_FACTORS, OPTION_5_OUTPUT_TIERS_FILE, OPTION_5_GEOMETRY_REFERENCE_FILE, OPTION_5_VIEW_VALID_GEOMETRIES):
    # Define the path to the GeoJSON file
    geojson_path = OPTION_5_USER_GEOMETRIES_GEOJSON_FILE

    # open the file
    try:
        geojson_data = gpd.read_file(geojson_path)
        print("... Read in geometry file successfully.\n")
    except Exception as e:
        raise ValueError("Could not read the geometry geojson file. Please check the file name and geometry content. Full error: " + str(e))

    ########################################################################
    ## open atlite capacity factor data
    ########################################################################
    # open the averaged atlite capacity factor data
    atlite_capacity_factors, atlite_capacity_factors_avg = support_functions.create_average_capacity_factor_file_atlite(ATLITE_DUMMY_DATA, ATLITE_CAPACITY_FACTORS_FOLDERS,DUMMY_START_DATE,DUMMY_END_DATE,DUMMY_LATITUDE_BOTTOM,DUMMY_LATITUDE_TOP,DUMMY_LONGITUDE_LEFT,DUMMY_LONGITUDE_RIGHT,MAXIMUM_CAPACITY,DATA_VARIABLE_NAME,TIME_VARIABLE_NAME,AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION)
    print("... Read averaged atlite capacity factor data.\n")

    # Call the function to check if each geometry is within the bounds
    inside_or_outside = check_geojson_within_bounds(geojson_data, atlite_capacity_factors, AVG_ATLITE_LONGITUDE_VARIABLE_NAME, AVG_ATLITE_LATITUDE_VARIABLE_NAME)

    # Initialize a list to store visualization table data
    geometry_table_list = []

    # Initialize a list to store geometry layer data
    geometry_layer_list = []

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
    tier_data = {}
    for index, row in geojson_data.iterrows():
        # read geometry and metadata
        geometry_type = row['geometry'].geom_type
        is_within_bounds = inside_or_outside[index]
        tier_label = f'tier_{index + 1}'
        # Create a DataFrame with columns 'tier_1', 'tier_2', etc.


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
                potential_tier = calculate_valid_tiers(atlite_capacity_factors,row['geometry'],geometry_type, AVG_ATLITE_LATITUDE_VARIABLE_NAME, AVG_ATLITE_LONGITUDE_VARIABLE_NAME, AVG_ATLITE_DATA_VARIABLE_NAME)
                if potential_tier is not None:
                    tier_data[tier_label] = potential_tier
                    print("... Tier generated successfully for ",tier_label)
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
                potential_tier = calculate_valid_tiers(atlite_capacity_factors, row['geometry'], geometry_type, AVG_ATLITE_LATITUDE_VARIABLE_NAME, AVG_ATLITE_LONGITUDE_VARIABLE_NAME, AVG_ATLITE_DATA_VARIABLE_NAME)
                if potential_tier is not None:
                    tier_data[tier_label] = potential_tier
                    print("... Tier generated successfully for ",tier_label)
                    # otherwise, no tier for this point
                else:
                    print("... No tier for ", tier_label)

        else:
            # unknown geometry type
            print("... ",geometry_type," is not supported. Only POLYGON, or POINTS allowed.")


    # format the tier data for the tier piece selection
    print("\n... Finished compiling tier data successfully:")
    print(tier_data)
    valid_output_tiers = pd.DataFrame(tier_data)

    # check if output directories are created
    if not os.path.exists(OPTION_5_OUTPUT_FOLDER):
        os.makedirs(OPTION_5_OUTPUT_FOLDER)

    # scale capacity factors if required:
    if SCALE_CAPACITY_FACTORS.lower() == "true":
        valid_output_tiers = valid_output_tiers / float(MAXIMUM_CAPACITY)  # divide by the weightings
        print("\n... Capacity factors were scaled by division of maximum capacity:", MAXIMUM_CAPACITY)

    # for reference, save tiers to csv file
    valid_output_tiers.to_csv(os.path.join(OPTION_5_OUTPUT_FOLDER,OPTION_5_OUTPUT_TIERS_FILE))

    # Save valid geometries to file:
    # Convert the list of dictionaries to a pandas DataFrame
    geometry_table_df = pd.DataFrame(geometry_table_list)

    # Save the DataFrame to a CSV file
    geometry_table_df.to_csv(os.path.join(OPTION_5_OUTPUT_FOLDER,OPTION_5_GEOMETRY_REFERENCE_FILE))



    print("\n... Saved output tiers file to:",os.path.join(OPTION_5_OUTPUT_FOLDER,OPTION_5_OUTPUT_TIERS_FILE))
    print("... Tier generation completed successfully!")
    print("\nOption_5 completed successfully!")
    print("----------------------------------------------------------------\n")



    if OPTION_5_VIEW_VALID_GEOMETRIES.lower() == "true":
        print("\nVisualization starting up ...")
        # build the Atlite bounding box:
        geographical_bounds_atlite_data = [[min_latitude, min_longitude], [max_latitude, max_longitude]]
        #visualize with Dash
        visualize_geometries(geographical_bounds_atlite_data,geometry_table_list,valid_output_tiers,geometry_layer_list)
    else:
        print("\nNo visualization selected. If you want to visualize thedata set the OPTION_5_VIEW_VALID_GEOMETRIES to true.")

if __name__ == '__main__':
    print("Starting tier processing for Option 5: single tier per user defined geometry ...")
    # check args or load env file and run codes
    try:
        print("TRYING TO USE ARGUMENTS")
        args = parse_arguments()
        print("ARGUMENTS FOUND. USING ARGUMENTS")

        # RUN CODES
        option_5_process_geometries_into_tiers(**vars(args))
    except Exception as e:
        print("ARGUMENTS NOT FOUND: ",e)
        try:
            print("TRYING TO LOAD ENV FILE VARIABLES")
            # Load variables from the .env file
            args = load_from_env()
            print("ENV FILE FOUND. USING ENV FILE")

            # RUN CODES
            option_5_process_geometries_into_tiers(**args)

        except Exception as e:
            print("ENV FILE NOT FOUND: ",e)
            print("ERROR ... USER ARGS AND ENV FILE NOT FOUND, ABORTING!")
            raise ValueError("COULD NOT FIND ARGS OR LOAD ENV FILE. USER ARGS OR ENV FILE MISSING.")


    # args example use:
    # python Option_5_step2_tier_generation_average_per_geometry.py --AVG_ATLITE_LONGITUDE_VARIABLE_NAME longitude --AVG_ATLITE_LATITUDE_VARIABLE_NAME latitude --AVG_ATLITE_DATA_VARIABLE_NAME capacity_factors --OPTION_5_USER_GEOMETRIES_GEOJSON_FILE "assets/user_geometry/example.geojson" --ATLITE_DUMMY_DATA True  --DUMMY_START_DATE  '2023-01-01' --DUMMY_END_DATE '2024-01-01'  --DUMMY_LATITUDE_BOTTOM  -32 --DUMMY_LATITUDE_TOP -30  --DUMMY_LONGITUDE_LEFT 26  --DUMMY_LONGITUDE_RIGHT 28   --MAXIMUM_CAPACITY  50 --DATA_VARIABLE_NAME capacity_factors  --TIME_VARIABLE_NAME  time --AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION "assets/avg_atlite_capacity_factors.nc" --OPTION_5_OUTPUT_FOLDER "assets/option_5_output" --SCALE_CAPACITY_FACTORS True --OPTION_5_OUTPUT_TIERS_FILE "option_5_single_tiers_per_geometry.csv" --OPTION_5_GEOMETRY_REFERENCE_FILE "option_5_geometry_reference_file.csv" --OPTION_5_VIEW_VALID_GEOMETRIES False


