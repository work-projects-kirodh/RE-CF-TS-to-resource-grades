"""
Purpose: User can select the pieces of tiers they wish for the final selection of the capacity factors.

author: kirodh boodhraj
"""
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import folium
from folium import plugins
from folium.raster_layers import TileLayer
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import shape, box, Point, Polygon
import xarray as xr
import os
import temporary_data as temp_data
from dash import dash_table

################################
# Check geometries, inside or outside bounding box
################################

def check_geojson_within_bounds(geojson_data, xarray_dataset):
    # # Read GeoJSON file, send in read file already
    # geojson_data = gpd.read_file(geojson_path)

    # Get the bounds of the xarray dataset
    bounds = (xarray_dataset[os.environ.get("AVG_ATLITE_LONGITUDE_VARIABLE_NAME")].min(), xarray_dataset[os.environ.get("AVG_ATLITE_LATITUDE_VARIABLE_NAME")].min(), xarray_dataset[os.environ.get("AVG_ATLITE_LONGITUDE_VARIABLE_NAME")].max(), xarray_dataset[os.environ.get("AVG_ATLITE_LATITUDE_VARIABLE_NAME")].max())
    bounding_box = box(*bounds)

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

    return is_within_bounds_list

# Define the path to the GeoJSON file
geojson_path = os.environ.get("USER_GEOMETRIES_GEOJSON_FILE")

# open the file
geojson_data = gpd.read_file(geojson_path)

# TODO: Example xarray dataset (replace with your actual dataset)
atlite_capacity_factors = temp_data.create_dataset()

# Call the function to check if each geometry is within the bounds
inside_or_outside = check_geojson_within_bounds(geojson_data, atlite_capacity_factors)

# Print the result list
# print(inside_or_outside)



################################
## obtain the tier
################################
def calculate_tier(atlite_data,points_geometry,geometry):
    # returns a list of numbers for the tier
    # if point, then find the closest point on the grid and use this as the tier
    if geometry == "Point":
        # Find the nearest latitude and longitude in the xarray dataset
        # nearest_lat = atlite_data[os.environ.get("AVG_ATLITE_LATITUDE_VARIABLE_NAME")].sel(latitude=points_geometry.x, method='nearest').values
        # nearest_lon = atlite_data[os.environ.get("AVG_ATLITE_LONGITUDE_VARIABLE_NAME")].sel(longitude=points_geometry.y, method='nearest').values

        # Find the nearest latitude and longitude in the xarray dataset
        lat_index = np.abs(atlite_data[os.environ.get("AVG_ATLITE_LATITUDE_VARIABLE_NAME")] - points_geometry.y).argmin().item()
        lon_index = np.abs(atlite_data[os.environ.get("AVG_ATLITE_LONGITUDE_VARIABLE_NAME")] - points_geometry.x).argmin().item()

        # # Extract the nearest latitude and longitude values
        # nearest_lat = float(atlite_data[os.environ.get("AVG_ATLITE_LATITUDE_VARIABLE_NAME")].values[lat_index])
        # nearest_lon = float(atlite_data[os.environ.get("AVG_ATLITE_LONGITUDE_VARIABLE_NAME")].values[lon_index])

        # Select the data at the nearest point
        # capacity_factors_at_nearest_point = atlite_data[os.environ.get("AVG_ATLITE_DATA_VARIABLE_NAME")].sel(latitude=nearest_lat,longitude=nearest_lon,method='nearest')
        capacity_factors_at_nearest_point = atlite_data[os.environ.get("AVG_ATLITE_DATA_VARIABLE_NAME")][:,lat_index,lon_index] #.sel(latitude=nearest_lat,longitude=nearest_lon,method='nearest')
        return capacity_factors_at_nearest_point.values

    # TODO: else if it is a polygon, then find all coordinates within the polygon and then average spatially
    elif geometry == "Polygon":
        # Extract lat and lon values from the xarray dataset
        lats = atlite_data[os.environ.get("AVG_ATLITE_LATITUDE_VARIABLE_NAME")].values
        lons = atlite_data[os.environ.get("AVG_ATLITE_LONGITUDE_VARIABLE_NAME")].values

        # Create a list of Point objects for each (lat, lon) pair in the dataset
        points = [Point(lon, lat) for lat, lon in zip(lats, lons)]
        # print("points: ",points)
        # print("geometry: ",points_geometry)

        # Check which points lie within the polygon
        points_within_polygon = [point for point in points if point.within(points_geometry)]
        if points_within_polygon == []:
            return None

        # print("points_within_polygon",points_within_polygon)

        # Now you can use the indices of the points within the polygon to select data from the xarray dataset
        selected_data = atlite_data.sel(latitude=[point.y for point in points_within_polygon],longitude=[point.x for point in points_within_polygon])

        # Spatially average the selected data over lat and lon dimensions
        spatially_averaged_data = selected_data.mean(dim=[os.environ.get("AVG_ATLITE_LATITUDE_VARIABLE_NAME"), os.environ.get("AVG_ATLITE_LONGITUDE_VARIABLE_NAME")], skipna=True)
        return spatially_averaged_data[os.environ.get("AVG_ATLITE_DATA_VARIABLE_NAME")].values
    # else return nothing
    else:
        return None



################################
# dash app
################################


app = dash.Dash(__name__)

################################
# MAP
################################

m = folium.Map(location=[-30.5595, 22.9375], zoom_start=5,height="100%")

# Initialize a list to store table data
table_data = []

########################################################################
## Bounding box
########################################################################
# add the bounding box user should stay within
# Get the maximum and minimum latitude and longitude values
max_latitude = atlite_capacity_factors[os.environ.get("AVG_ATLITE_LATITUDE_VARIABLE_NAME")].max().values
min_latitude = atlite_capacity_factors[os.environ.get("AVG_ATLITE_LATITUDE_VARIABLE_NAME")].min().values
max_longitude = atlite_capacity_factors[os.environ.get("AVG_ATLITE_LONGITUDE_VARIABLE_NAME")].max().values
min_longitude = atlite_capacity_factors[os.environ.get("AVG_ATLITE_LONGITUDE_VARIABLE_NAME")].min().values

# rectangle polygon
user_bound_frame = folium.Rectangle(
    bounds=[[min_latitude, min_longitude], [max_latitude, max_longitude]],
    color='blue',
    fill=False,
    weight=5,
    opacity=1.0,
    popup=folium.Popup('Valid points and polygons lie within this bounding box!', parse_html=True),  # Add a message to the rectangle
)
user_bound_frame.add_to(m)


# Loop through each geometry in the GeoJSON file
# add table entry and geometry on map and create tiers data
tier_data = {}
for index, row in geojson_data.iterrows():
    geometry_type = row['geometry'].geom_type
    is_within_bounds = inside_or_outside[index] # bounding_box.intersects(row['geometry']) and row['geometry'].within(bounding_box)
    tier_label = f'tier_{index + 1}'
    # Create a DataFrame with columns 'tier_1', 'tier_2', etc.


    # Add geometry to the Folium map with styling based on conditions
    if geometry_type == 'Polygon':
        folium.Polygon(
            locations=[x[::-1] for x in list(row['geometry'].exterior.coords)], # swap the lon/lat, or else wrong place on world
            color='green' if is_within_bounds else 'red',
            fill=True,
            fill_color='green' if is_within_bounds else 'red',
            fill_opacity=0.5,
            dash_array='dashed' if not is_within_bounds else 'solid',
            popup=tier_label  # Add popup with tier label
        ).add_to(m)

        # Populate the table data for each geometry
        table_data.append({
            'Tier': tier_label,
            'Geometry Type': geometry_type,
            'Coordinates': str(row['geometry']),
            'Result': 'Inside' if is_within_bounds else 'Outside',
        })

        # generate tier data if inside the bounding box
        if is_within_bounds:
            print("------------------------------------------------")
            print("POLYGON",tier_label)
            potential_tier = calculate_tier(atlite_capacity_factors,row['geometry'],geometry_type)
            if potential_tier is not None:
                tier_data[tier_label] = potential_tier
                # otherwise no tier for this point


    elif geometry_type == 'LineString':
        folium.PolyLine(
            locations=[x[::-1] for x in list(row['geometry'].coords)],
            color='red',
            dash_array='dashed',
            popup=tier_label  # Add popup with tier label
        ).add_to(m)

        # Populate the table data for each geometry
        table_data.append({
            'Tier': tier_label,
            'Geometry Type': geometry_type,
            'Coordinates': str(row['geometry']),
            'Result': 'Outside',
        })

        # no tiers for line strings
    elif geometry_type == 'Point':
        folium.CircleMarker(
            location=list(row['geometry'].coords)[0][::-1],
            radius=5,
            color='green' if is_within_bounds else 'red',
            fill=True,
            fill_color='green' if is_within_bounds else 'red',
            dash_array='dashed' if not is_within_bounds else 'solid',
            popup=tier_label  # Add popup with tier label
        ).add_to(m)

        # Populate the table data for each geometry
        table_data.append({
            'Tier': tier_label,
            'Geometry Type': geometry_type,
            'Coordinates': str(row['geometry']),
            'Result': 'Inside' if is_within_bounds else 'Outside',
        })

        # generate tier data
        if is_within_bounds:
            print("------------------------------------------------")
            print("POINT", tier_label)
            potential_tier = calculate_tier(atlite_capacity_factors, row['geometry'], geometry_type)
            if potential_tier is not None:
                tier_data[tier_label] = potential_tier
                # otherwise no tier for this point


# format the tier data for the tier piece selection
# print(tier_data)
tiers = pd.DataFrame(tier_data)
tiers = tiers.div(float(os.environ.get("MAXIMUM_CAPACITY"))) # divide by the weightings
# for reference, save tiers to csv file
tiers.to_csv(os.environ.get("TIER_FILE_STORAGE"),index=False)
print(tiers)



### Layout elemets

#######################################
## Header, footer, spacing
#######################################

# HEADER
main_header = html.Div(
    [
        html.H1("Please validate your geometries here (polygons and points), lines excluded.", style={'textAlign': 'center', 'color': 'white', 'background-color': 'lightgreen', 'padding': '20px'}),
        html.Ul([
            html.Li("1. Verify if your polygons or points lie within the bounding box."),
            html.Li("2. The polygons/points within the bounding box will be green and are valid tiers. Note that not all polygons will have data points within them and no tier will be created."),
            html.Li("3. Go to the section below to select the capacity factors.")
        ], style={'list-style-type': 'none', 'margin': '30px','background-color': 'lightblue', 'padding': '30px'}),
    ],
    style={'margin-top': '20px', 'margin-bottom': '20px'}
)

second_header = html.Div(
    [
        html.H1("Please select your tier pieces here.", style={'textAlign': 'center', 'color': 'white', 'background-color': 'lightgreen', 'padding': '20px'}),
        html.Ul([
            html.Li("1. The valid tiers are shown in the table below. The graph has all the tiers plotted."),
            html.Li("2. Select indexes corresponding to timestep to choose the piece of tier you would like. First then second index should be integers Use the dropdown to select the actual tier. All other entries are ignored."),
            html.Li("3. Note if there are any overlapping tiers or missing indexes, the generate tier button will not be active.")
        ], style={'list-style-type': 'none', 'margin': '30px','background-color': 'lightblue', 'padding': '30px'}),
    ],
    style={'margin-top': '20px', 'margin-bottom': '20px'}
)

# FOOTER
footer = html.Div(
    [
        html.Img(src=app.get_asset_url('csir_logo.jpg'), style={'width': '150px', 'height': 'auto', 'margin-right': '20px'}),
        html.Img(src=app.get_asset_url('leapre_logo.jpg'), style={'width': '150px', 'height': 'auto', 'margin-left': '20px'}),
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
        data=table_data,
        style_table={'width': '80%', 'margin': '0 auto'},
        style_cell={'textAlign': 'center'},
        style_data_conditional=[
            {
                'if': {'column_id': 'Result'},
                'color': 'green',
            },
            {
                'if': {'column_id': 'Result', 'filter_query': '{Result} eq "Outside"'},
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
## Second section
#######################################

valid_tiers = html.Div([
    html.Div(
        id='valid-tiers',
        style={
            'text-align': 'center',
            'border': '2px solid #4CAF50',  # Green border color
            'border-radius': '10px',  # Rounded corners
            'padding': '10px',  # Padding inside the box
            'background-color': '#87CEFA',  # Light blue background color
            'width': '300px',  # Adjust box width
            'margin': '0 auto',  # Center the box horizontally
        },
        children=[
            html.H3("Valid tiers for selection", style={'margin-bottom': '10px'}),
            html.Ul(id='tiers-list', children=[html.Li(i) for i in tiers.columns],style={'padding-inline-start': '0', 'list-style-type': 'none'},),
        ],
    ),
])


## graph preparation:
# Create traces for each tier
traces = []
for column in tiers.columns:
    trace = dict(
        x=tiers.index,
        y=tiers[column],
        mode='lines',
        name=column,
        opacity=0.5,
    )
    traces.append(trace)

# Extra space percentage (adjust as needed)
extra_space_percentage = 10

# Calculate the range with extra space
max_value = tiers.max().max()
min_value = tiers.min().min()
value_range = max_value - min_value
extra_space = value_range * (extra_space_percentage / 100)
y_axis_range = [min_value - extra_space, max_value + extra_space]

# Layout for the graph
layout = dict(
    title='Atlite Tiers',
    xaxis=dict(title='Index'),
    yaxis=dict(title='Scaled Capacity factor (MW/MW)', range=y_axis_range),
    legend=dict(orientation='h'),
)

# Plotly figure
fig = dict(data=traces, layout=layout)

# Initial table rows for table
initial_rows = 5
# graph and table
graph_and_table = html.Div([

    html.Div([
    # Graph
    dcc.Graph(id='tier-graph',figure=fig),
    ],style={'text-align': 'center','margin-left': '10vw','margin-right': '10vw'}),


    # Table
    html.Div([
        html.H1("Insert index pieces here:"),
        dash_table.DataTable(
            id='index-table',
            columns=[
                {'name': 'First Index', 'id': 'first_index', 'editable': True},
                {'name': 'Second Index', 'id': 'second_index', 'editable': True},
                {'name': 'Tier', 'id': 'tier', 'presentation': 'dropdown'},
            ],
            data=[{'first_index': '', 'second_index': '', 'tier': ''} for _ in range(initial_rows)],
            editable=True,
            row_deletable=True,
            style_header={'text-align': 'center', 'font-size': '16px', 'font-weight': 'bold'},
            dropdown={
                'tier': {
                    'options': [{'label': tier_column, 'value': tier_column} for tier_column in tiers.columns]
                },
            }
        ),

        # Add row button
        html.Button('Add Row', id='add-row-button', n_clicks=0, style={'margin-top': '10px', 'background-color': '#87CEFA', 'padding': '10px', 'width': '200px'}),

        # Hidden div to store added rows
        html.Div(id='added-rows', style={'display': 'none'}),
    ],style={'text-align': 'center','margin-left': '30vw','margin-right': '30vw'}),


    # Add row button
    html.Button('Generate Final Capacity Factors', id='capacity-factor-button', n_clicks=0,disabled=True,
                style={'margin-top': '10px', 'background-color': '#87CEFA', 'padding': '10px', 'width': '200px'}),

    # Missing and Overlapping Indexes
    html.Div(id='index-status',
             style={'text-align': 'center', 'margin-left': '10vw', 'margin-right': '10vw', 'margin-top': '5vw'}),

],style={'text-align': 'center'})


#######################################
## Pull all layout elements together
#######################################

# App layout
app.layout = html.Div([
    # geometry validation
    main_header,
    table_layout,
    spacing,
    map_layout,
    spacing,
    # tier pieces
    second_header,
    spacing,
    valid_tiers,
    spacing,
    graph_and_table,
    spacing,
    footer
])



#################################################
## callbacks
#################################################

# Callback to update missing and overlapping indexes
@app.callback(
    Output('index-status', 'children'),
    Input('index-table', 'data'),
)
def update_index_status(data):
    # Filter out rows with empty values
    filtered_data = [row for row in data if all(row.values())]

    # Extract entries with integer first and second indexes
    integer_entries = [(int(row['first_index']), int(row['second_index'])) for row in filtered_data
                       if row['first_index'].isdigit() and row['second_index'].isdigit()]

    # Extract all unique indexes
    all_indexes = set(index for entry in integer_entries for index in entry)

    # Calculate missing and overlapping indexes
    missing_indexes = set(range(len(tiers))) - all_indexes
    overlapping_indexes = set(index for index in all_indexes if all_indexes.count(index) > 1)

    # Display missing indexes in green and overlapping indexes in red
    status_text = [
        html.Span(f'Missing Indexes: {missing_indexes}', style={'color': 'green'}),
        html.Br(),
        html.Span(f'Overlapping Indexes: {overlapping_indexes}', style={'color': 'red'}),
    ]

    return status_text


# Callback to update the graph based on table data
@app.callback(
    Output('tier-graph', 'figure'),
    Input('index-table', 'data'),
    State('tier-graph', 'figure')
)
def update_graph(data,previous_fig):
    # Filter out rows with empty values
    filtered_data = [row for row in data if all(row.values())]

    # Extract selected tiers and indices
    tiers = [row['tier'] for row in filtered_data]
    try:
        indices = [(int(row['first_index']), int(row['second_index'])) for row in filtered_data]
    except TypeError:
        indices = (0, 0)  # Provide default values or handle accordingly

    # indices = [(int(row['first_index']), int(row['second_index'])) for row in filtered_data]

    # Create line traces
    traces = [dict(x=list(range(len(tiers))), y=tiers[tier], name=tier) for tier in tiers]

    # Create graph layout
    layout = dict(
        title='Atlite Tiers',
        xaxis=dict(title='Index'),
        yaxis=dict(title='Scaled Capacity factor (MW/MW)'),
        legend=dict(orientation='h'),
    )

    return previous_fig



# Callback to update added rows
@app.callback(
    Output('index-table', 'data'),
    Input('add-row-button', 'n_clicks'),
    [State('index-table', 'data'),]
)
def add_row(n_clicks,table_data):
    # print(table_data,n_clicks)
    if n_clicks > 0:
        table_data.append({'first_index': '', 'second_index': '', 'tier': ''})
    return table_data




if __name__ == '__main__':
    app.run_server(debug=True)



# app = dash.Dash(__name__)
#
#
# # Define the layout of the Dash app
# app.layout = html.Div([
#     # HEADER
#     html.Div(
#         [
#             html.H1("Please select your tiers here (polygons or points)", style={'textAlign': 'center', 'color': 'white', 'background-color': 'lightgreen', 'padding': '20px'}),
#             html.Ul([
#                 html.Li("1. First select your tiers within the demarcated area. Note circles are considered points. Use polygon to capture areas."),
#                 html.Li("2. Second click export on the map"),
#                 html.Li("3. Third copy the geojson file into the current working directory and run the tier_generation script")
#             ], style={'list-style-type': 'none', 'margin': '30px','background-color': 'lightblue', 'padding': '30px'}),
#         ],
#         style={'margin-top': '20px', 'margin-bottom': '20px'}
#     ),
#     # MAP
#     html.Div(
#         html.Iframe(id='map', srcDoc=m._repr_html_(), width='70%', height='650', style={'margin': '0 auto'}),
#         style={'textAlign': 'center'},
#     ),
#     # SPACING
#     html.Div(style={'bottom': 0, 'width': '90%', 'padding': '20px', 'background-color': 'white', 'text-align': 'center'}),
#     # FOOTER
#     html.Div(
#         [
#             html.Img(src=app.get_asset_url('csir_logo.jpg'), style={'width': '150px', 'height': 'auto', 'margin-right': '20px'}),
#             html.Img(src=app.get_asset_url('leapre_logo.jpg'), style={'width': '150px', 'height': 'auto', 'margin-left': '20px'}),
#         ],
#         style={'bottom': 0, 'width': '95vw', 'padding': '20px', 'background-color': 'lightgray', 'text-align': 'center'}
#     )
# ])
#
#
# if __name__ == '__main__':
#     app.run_server(debug=True)
