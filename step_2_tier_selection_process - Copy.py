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
import pandas as pd

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
world_atlas_capacity_factor_file = 'assets/world_atlas_capacity_factors.png'

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
            'capacity_factors': (['time', 'latitude', 'longitude'],
                                 np.zeros((len(hourly_date_times), len(latitude_intervals), len(longitude_intervals))))
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
    return atlite_capacity_factors
start_date = '2023-01-01'
end_date = '2024-01-01'
bounding_box = {
    'latitudes': (-40.0, -20.0),
    'longitudes': (10.0, 40.0)
}
cf = create_dataset(start_date, end_date, bounding_box['latitudes'], bounding_box['longitudes'])
# print(cf['capacity_factors'].data)

data_at_timestep = cf.isel(time=0)
# Assuming data has latitude ('lat'), longitude ('lon'), and the variable of interest ('variable')
latitude = data_at_timestep['latitude'].values.astype(float)
longitude = data_at_timestep['longitude'].values.astype(float)
values = data_at_timestep['capacity_factors'].values.astype(float)
values[np.isnan(values)] = 0.0  # Replace NaN with 0.0, you can choose a different value if needed
# print(type(latitude),longitude)
# print(type(values))

# Create a meshgrid of longitude and latitude
lon, lat = np.meshgrid(longitude, latitude)

# Generate random altitude values for demonstration purposes
data = list(zip(lat.flatten(), lon.flatten(), values.flatten()))



# print(heatmap_data)
plugins.HeatMap(data, name='atlite',opacity=0.3).add_to(m)



## add netcdf
# Assuming ds is your xarray dataset
ds = xr.open_dataset('assets/world_atlas_capacity_factors.nc')

# Select every fifth latitude and longitude along with capacity_factor
ds_subset = ds.sel(lat=ds.lat.values[::15], lon=ds.lon.values[::15])

# Access the capacity_factor variable from the subset
capacity_factor_subset = ds_subset
latitude_c = capacity_factor_subset['lat'].values.astype(float)
longitude_c = capacity_factor_subset['lon'].values.astype(float)
values_c = capacity_factor_subset['Band1'].values.astype(float)
values_c[np.isnan(values_c)] = 0.0  # Replace NaN with 0.0, you can choose a different value if needed
lon_c, lat_c = np.meshgrid(longitude_c, latitude_c)
data_c = list(zip(lat_c.flatten(), lon_c.flatten(), values_c.flatten()))
plugins.HeatMap(data_c, name='atlas',opacity=0.3).add_to(m)

# Add a custom legend to the map
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
            html.Img(src=app.get_asset_url('csir_logo.jpg'), style={'width': '150px', 'height': 'auto', 'margin-right': '20px'}),
            html.Img(src=app.get_asset_url('leapre_logo.jpg'), style={'width': '150px', 'height': 'auto', 'margin-left': '20px'}),
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
