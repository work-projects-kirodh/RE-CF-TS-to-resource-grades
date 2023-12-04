import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import folium
from folium import plugins
from folium.raster_layers import TileLayer
import rasterio
from rasterio.plot import reshape_as_image
from PIL import Image
import numpy as np
from pyproj import Transformer
import geopandas as gpd
from rasterio.windows import Window
import io
import xarray as xr
import base64

app = dash.Dash(__name__)

# Create a Folium map centered around South Africa
m = folium.Map(location=[-30.5595, 22.9375], zoom_start=5,height="100%")  # South Africa's approximate center

# Add the Leaflet.draw plugin
draw = plugins.Draw(export=True)
draw.add_to(m)

# Create FeatureGroups for each layer
user_bound_layer = folium.FeatureGroup(name='User Bounding Box')
world_atlas_layer = folium.FeatureGroup(name='World Atlas Capacity Factors')


# add the bounding box user should stay within
# Add a frame around user bounds
# CHANGE THESE FOR THE WINDOW FOR USER SELECTION
left = 17
right = 33
top = -22
bottom = -35

south_africa_frame = folium.Rectangle(
    bounds=[[bottom, left], [top, right]],
    color='red',
    fill=False,
    weight=2,
    opacity=0.7,
    popup=folium.Popup('Put your points and polygons within this bounding box!', parse_html=True),  # Add a message to the rectangle
)
# south_africa_frame.add_to(m)
south_africa_frame.add_to(user_bound_layer)


# add the world atlas capacity factor to the map
world_atlas_capacity_factor_file = 'assets/capacity_factors.png'

world_file_params = [2381.93855019098555204, 0, 0, -2381.93855019098555204, 1079888.20687509560957551, -2294353.40437131375074387]
# CHANGE THESE FOR FITTING WORLD ATLAS
# Specify the geographical bounds of the PNG file
left, bottom, right, top = 9.6,-35.8,37.8,-20.0

image_overlay = folium.raster_layers.ImageOverlay(
    image=world_atlas_capacity_factor_file,
    bounds = [[bottom, left], [top, right]],
    opacity=0.3,
    interactive=True,
    # mercator_project=True,  #errors if uncomment! Specify that the projection is mercator
    world_file_params=world_file_params,
)
# image_overlay.add_to(m)
image_overlay.add_to(world_atlas_layer)




# Add FeatureGroups to the map
user_bound_layer.add_to(m)
world_atlas_layer.add_to(m)
# Add layer control to the map
folium.LayerControl().add_to(m)


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
            html.Img(src=app.get_asset_url('csirlogo.jpg'), style={'width': '150px', 'height': 'auto', 'margin-right': '20px'}),
            html.Img(src=app.get_asset_url('leapre.jpg'), style={'width': '150px', 'height': 'auto', 'margin-left': '20px'}),
        ],
        style={'bottom': 0, 'width': '95vw', 'padding': '20px', 'background-color': 'lightgray', 'text-align': 'center'}
    )
])

# # Define the callback to close the map when the button is clicked
# @app.callback(
#     Output('map', 'srcDoc'),
#     [Input('map', 'relayoutData')],
#     [State('map', 'srcDoc')]
# )
# def create_tier_zones(relayoutData, old_map):
#     if relayoutData and 'drawnLayer' in relayoutData:
#         print("Map exported")
#         # Print the drawn features
#         print(relayoutData['drawnLayer']['features'])
#         # You can save the drawn features to a geojson file or perform other actions here
#     return old_map  # m._repr_html_()

if __name__ == '__main__':
    app.run_server(debug=True)
