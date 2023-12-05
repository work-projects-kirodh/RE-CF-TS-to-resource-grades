import os

import dash
from dash import html
import folium
from folium import plugins
import numpy as np
import xarray as xr
import pandas as pd
from dotenv import load_dotenv


# Load variables from the .env file
load_dotenv()

################################################################
## Dash App
################################################################

# create dash app
app = dash.Dash(__name__)



########################################################################
## open atlite capacity factor data
########################################################################
# open the averaged atlite capacity factor data
# Get the environment variable
atlite_filepath_env = os.environ.get("AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION")

atlite_avg_capacity_factor_data = xr.open_dataset(atlite_filepath_env)
# print(atlite_avg_capacity_factor_data)


########################################################################
## MAP
########################################################################
# Create a Folium map centered around South Africa
m = folium.Map(location=[-30.5595, 22.9375], zoom_start=5,height="100%")  # South Africa's approximate center

# Add the Leaflet.draw plugin
draw = plugins.Draw(export=True)
draw.add_to(m)

# Create FeatureGroups for each layer
user_bound_layer_polygon = folium.FeatureGroup(name='User Bounding Box')
world_atlas_layer_png = folium.FeatureGroup(name='World Atlas Capacity Factors PNG')
world_atlas_layer_heatmap = folium.FeatureGroup(name='World Atlas Capacity Factors Heatmap')
atlite_layer_heatmap = folium.FeatureGroup(name='Atlite Capacity Factors Heatmap')


########################################################################
## Atlite heatmap layer
########################################################################
# file already open fom at top of code used for bounding box
# Extract the data
latitude_a = atlite_avg_capacity_factor_data[os.environ.get("AVG_ATLITE_LATITUDE_VARIABLE_NAME")].values.astype(float)
longitude_a = atlite_avg_capacity_factor_data[os.environ.get("AVG_ATLITE_LONGITUDE_VARIABLE_NAME")].values.astype(float)
values_a = atlite_avg_capacity_factor_data[os.environ.get("AVG_ATLITE_DATA_VARIABLE_NAME")].values.astype(float)
values_a[np.isnan(values_a)] = 0.0  # Replace NaN with 0.0, you can choose a different value if needed

# Create a meshgrid of longitude and latitude
lon_a, lat_a = np.meshgrid(longitude_a, latitude_a)

# Generate random altitude values for demonstration purposes
data_a = list(zip(lat_a.flatten(), lon_a.flatten(), values_a.flatten()))

# add to map layer
plugins.HeatMap(data_a, name='atlite',opacity=0.3).add_to(atlite_layer_heatmap)


########################################################################
## Bounding box
########################################################################
# add the bounding box user should stay within
# Get the maximum and minimum latitude and longitude values
max_latitude = atlite_avg_capacity_factor_data.latitude.max().values
min_latitude = atlite_avg_capacity_factor_data.latitude.min().values
max_longitude = atlite_avg_capacity_factor_data.longitude.max().values
min_longitude = atlite_avg_capacity_factor_data.longitude.min().values

# rectangle polygon
user_bound_frame = folium.Rectangle(
    bounds=[[min_latitude, min_longitude], [max_latitude, max_longitude]],
    color='blue',
    fill=False,
    weight=5,
    opacity=1.0,
    popup=folium.Popup('Put your points and polygons within this bounding box!', parse_html=True),  # Add a message to the rectangle
)
# south_africa_frame.add_to(m)
user_bound_frame.add_to(user_bound_layer_polygon)

########################################################################
## World Atlas PNG layer
########################################################################
# add the world atlas capacity factor to the map
world_atlas_capacity_factor_file = os.environ.get("WORLD_ATLAS_CAPACITY_FACTORS_PNG_FILE_LOCATION")

# world_file_params = [2381.93855019098555204, 0, 0, -2381.93855019098555204, 1079888.20687509560957551, -2294353.40437131375074387]
# Specify the geographical bounds of the PNG file
# left, bottom, right, top = 9.6,-35.8,37.8,-20.0
png_left, png_bottom, png_right, png_top = float(os.environ.get("WORLD_ATLAS_PNG_LONGITUDE_LEFT")),\
                           float(os.environ.get("WORLD_ATLAS_PNG_LATITUDE_BOTTOM")),\
                           float(os.environ.get("WORLD_ATLAS_PNG_LONGITUDE_RIGHT")),\
                           float(os.environ.get("WORLD_ATLAS_PNG_LATITUDE_TOP"))

# build layer
world_atlas_png_overlay = folium.raster_layers.ImageOverlay(
    image=world_atlas_capacity_factor_file,
    bounds = [[png_bottom, png_left], [png_top, png_right]],
    opacity=0.3,
    interactive=True,
    # mercator_project=True,  #errors if uncomment! Specify that the projection is mercator
    # world_file_params=world_file_params,
)
# image_overlay.add_to(m)
world_atlas_png_overlay.add_to(world_atlas_layer_png)

########################################################################
## World Atlas heatmap layer
########################################################################
# get down scaling resolution of world atlas netcdf i.e. number of points to skip for lat lon values in array, to make things render faster
world_atlas_resolution_reduction = int(os.environ.get("WORLD_ATLAS_RESOLUTION_REDUCTION"))
# open world atlas netcdf
world_atlas_netcdf = xr.open_dataset(os.environ.get("WORLD_ATLAS_CAPACITY_FACTORS_HEATMAP_FILE_LOCATION"))

# Select every world_atlas_resolution_reduction latitude and longitude along with capacity_factor
capacity_factor_subset = world_atlas_netcdf.sel(lat=world_atlas_netcdf.lat.values[::world_atlas_resolution_reduction], lon=world_atlas_netcdf.lon.values[::world_atlas_resolution_reduction])

# Access the capacity_factor variable from the subset
latitude_wa = capacity_factor_subset[os.environ.get("WORLD_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME")].values.astype(float)
longitude_wa = capacity_factor_subset[os.environ.get("WORLD_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME")].values.astype(float)
values_wa = capacity_factor_subset[os.environ.get("WORLD_ATLAS_HEATMAP_DATA_VARIABLE_NAME")].values.astype(float)
values_wa[np.isnan(values_wa)] = 0.0  # Replace NaN with 0.0, you can choose a different value if needed
lon_wa, lat_wa = np.meshgrid(longitude_wa, latitude_wa)
# serialize data for folium
data_wa = list(zip(lat_wa.flatten(), lon_wa.flatten(), values_wa.flatten()))
# add to map layer
plugins.HeatMap(data_wa, name='atlas',opacity=0.3).add_to(world_atlas_layer_heatmap)



########################################################################
## MAP: Add legends, order the layers
########################################################################

# Add a custom legend to the map
legend_html = """
     <div style="position: fixed; 
                 bottom: 50px; right: 50px; width: 160px; height: 100px; 
                 background-color: white; border:2px solid grey; z-index:9999; 
                 font-size:14px; text-align: left; padding: 5px;">
         <div style="display: flex; justify-content: space-between;">
             <div style="width: 20px; height: 20px; background-color: blue; border: 1px solid black; display: inline-block;"></div>
             <div style="width: 100px; display: inline-block;">Low</div>
         </div>
         <div style="display: flex; justify-content: space-between;">
             <div style="width: 20px; height: 20px; background-color: green; border: 1px solid black; display: inline-block;"></div>
             <div style="width: 100px; display: inline-block;">Medium</div>
         </div>
         <div style="display: flex; justify-content: space-between;">
             <div style="width: 20px; height: 20px; background-color: yellow; border: 1px solid black; display: inline-block;"></div>
             <div style="width: 100px; display: inline-block;">High</div>
         </div>
         <div style="display: flex; justify-content: space-between;">
             <div style="width: 20px; height: 20px; background-color: red; border: 1px solid black; display: inline-block;"></div>
             <div style="width: 100px; display: inline-block;">Very High</div>
         </div>
     </div>
"""
m.get_root().html.add_child(folium.Element(legend_html))


# Add FeatureGroups to the map, order matters!
world_atlas_layer_png.add_to(m)
world_atlas_layer_heatmap.add_to(m)
atlite_layer_heatmap.add_to(m)
user_bound_layer_polygon.add_to(m)

# Add layer control to the map
folium.LayerControl().add_to(m)


################################################################
## Dash App Layout
################################################################

# Define the layout of the Dash app
app.layout = html.Div([
    # HEADER
    html.Div(
        [
            html.H1("Please select your tiers here (polygons or points)", style={'textAlign': 'center', 'color': 'white', 'background-color': 'lightgreen', 'padding': '20px'}),
            html.Ul([
                html.Li("1. First select your tiers within the demarcated area. Note circles are considered points. Use polygon to capture areas."),
                html.Li("2. Second click export on the map"),
                html.Li("3. Third copy the geojson file into the current working directory and run the tier_generation script")
            ], style={'list-style-type': 'none', 'margin': '30px','background-color': 'lightblue', 'padding': '30px'}),
        ],
        style={'margin-top': '20px', 'margin-bottom': '20px'}
    ),
    # MAP
    html.Div(
        html.Iframe(id='map', srcDoc=m._repr_html_(), width='70%', height='650', style={'margin': '0 auto'}),
        style={'textAlign': 'center'},
    ),
    # SPACING
    html.Div(style={'bottom': 0, 'width': '90%', 'padding': '20px', 'background-color': 'white', 'text-align': 'center'}),
    # FOOTER
    html.Div(
        [
            html.Img(src=app.get_asset_url('csir_logo.jpg'), style={'width': '150px', 'height': 'auto', 'margin-right': '20px'}),
            html.Img(src=app.get_asset_url('leapre_logo.jpg'), style={'width': '150px', 'height': 'auto', 'margin-left': '20px'}),
        ],
        style={'bottom': 0, 'width': '95vw', 'padding': '20px', 'background-color': 'lightgray', 'text-align': 'center'}
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
