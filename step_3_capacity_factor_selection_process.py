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
    bounds = (xarray_dataset.longitude.min(), xarray_dataset.latitude.min(), xarray_dataset.longitude.max(), xarray_dataset.latitude.max())
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
        nearest_lat = atlite_data.latitude.sel(latitude=points_geometry.x, method='nearest').values
        nearest_lon = atlite_data.longitude.sel(longitude=points_geometry.y, method='nearest').values

        # Select the data at the nearest point
        capacity_factors_at_nearest_point = atlite_capacity_factors.capacity_factors.sel(latitude=nearest_lat,longitude=nearest_lon,method='nearest')
        return capacity_factors_at_nearest_point.values

    # TODO: else if it is a polygon, then find all coordinates within the polygon and then average spatially
    elif geometry == "Polygon":
        # Extract lat and lon values from the xarray dataset
        lats = atlite_data[os.environ.get("AVG_ATLITE_LATITUDE_VARIABLE_NAME")].values
        lons = atlite_data[os.environ.get("AVG_ATLITE_LONGITUDE_VARIABLE_NAME")].values
        # lons = atlite_data['longitude'].values

        # Create a list of Point objects for each (lat, lon) pair in the dataset
        points = [Point(lon, lat) for lat, lon in zip(lats, lons)]

        # Check which points lie within the polygon
        points_within_polygon = [point for point in points if point.within(points_geometry)]

        # Now you can use the indices of the points within the polygon to select data from the xarray dataset
        selected_data = atlite_capacity_factors.sel(latitude=[point.y for point in points_within_polygon],
                                                    longitude=[point.x for point in points_within_polygon])

        # Spatially average the selected data over lat and lon dimensions
        spatially_averaged_data = selected_data.mean(dim=['latitude', 'longitude'], skipna=True)
        return spatially_averaged_data["capacity_factors"].values
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
max_latitude = atlite_capacity_factors.latitude.max().values
min_latitude = atlite_capacity_factors.latitude.min().values
max_longitude = atlite_capacity_factors.longitude.max().values
min_longitude = atlite_capacity_factors.longitude.min().values

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
    tier_label = f'Tier {index + 1}'
    # Create a DataFrame with columns 'tier_1', 'tier_2', etc.


    # Add geometry to the Folium map with styling based on conditions
    if geometry_type == 'Polygon':
        folium.Polygon(
            locations=[x[::-1] for x in list(row['geometry'].exterior.coords)], # swap the lon/lat, or else wrong p[lace on world
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
            tier_data[tier_label] = calculate_tier(atlite_capacity_factors,row['geometry'],geometry_type)

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
            tier_data[tier_label] = calculate_tier(atlite_capacity_factors,row['geometry'],geometry_type)


# format the tier data for the tier piece selection
print(tier_data)
tiers = pd.DataFrame(tier_data)
tiers = tiers.div(float(os.environ.get("MAXIMUM_CAPACITY"))) # divide by the weightings

### Layout elemets
# HEADER
main_header = html.Div(
    [
        html.H1("Please validate your geometries here (polygons and points), lines excluded.", style={'textAlign': 'center', 'color': 'white', 'background-color': 'lightgreen', 'padding': '20px'}),
        html.Ul([
            html.Li("1. Verify if your polygons or points lie within the bounding box."),
            html.Li("2. The polygons/points within the bounding box will be green and are valid tiers."),
            html.Li("3. Go to the section below to select the capacity factors.")
        ], style={'list-style-type': 'none', 'margin': '30px','background-color': 'lightblue', 'padding': '30px'}),
    ],
    style={'margin-top': '20px', 'margin-bottom': '20px'}
)

second_header = html.Div(
    [
        html.H1("Please select your tier pieces here.", style={'textAlign': 'center', 'color': 'white', 'background-color': 'lightgreen', 'padding': '20px'}),
        html.Ul([
            html.Li("1. ???."),
            html.Li("2. ???."),
            html.Li("3. ???.")
        ], style={'list-style-type': 'none', 'margin': '30px','background-color': 'lightblue', 'padding': '30px'}),
    ],
    style={'margin-top': '20px', 'margin-bottom': '20px'}
)

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

# SPACING
spacing = html.Div(style={'bottom': 0, 'width': '90%', 'padding': '20px', 'background-color': 'white', 'text-align': 'center'})


# FOOTER
footer = html.Div(
    [
        html.Img(src=app.get_asset_url('csir_logo.jpg'), style={'width': '150px', 'height': 'auto', 'margin-right': '20px'}),
        html.Img(src=app.get_asset_url('leapre_logo.jpg'), style={'width': '150px', 'height': 'auto', 'margin-left': '20px'}),
    ],
    style={'bottom': 0, 'width': '95vw', 'padding': '20px', 'background-color': 'lightgray', 'text-align': 'center'}
)

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
    footer
])



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
