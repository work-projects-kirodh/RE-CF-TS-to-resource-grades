import os

import dash
from dash import html
import folium
from folium import plugins
import numpy as np
import xarray as xr
from dotenv import load_dotenv

import Option_Support_Functions as support_functions


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
atlite_capacity_factors, atlite_capacity_factors_avg = support_functions.create_average_capacity_factor_file_atlite()
print("... Read averaged atlite capacity factor data.")



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
wind_atlas_layer_png = folium.FeatureGroup(name='Wind Atlas Capacity Factors PNG')
wind_atlas_layer_heatmap = folium.FeatureGroup(name='Wind Atlas Capacity Factors Heatmap')
atlite_layer_heatmap = folium.FeatureGroup(name='Atlite Capacity Factors Heatmap')


########################################################################
## Atlite heatmap layer
########################################################################
# file already open from at top of code used for bounding box
# Extract the data
latitude_a = atlite_capacity_factors_avg[os.environ.get("AVG_ATLITE_LATITUDE_VARIABLE_NAME")].values.astype(float)
longitude_a = atlite_capacity_factors_avg[os.environ.get("AVG_ATLITE_LONGITUDE_VARIABLE_NAME")].values.astype(float)
# values_a = atlite_capacity_factors_avg[os.environ.get("AVG_ATLITE_DATA_VARIABLE_NAME")].values.astype(float)
values_a = atlite_capacity_factors_avg.values.astype(float)
values_a[np.isnan(values_a)] = 0.0  # Replace NaN with 0.0, you can choose a different value if needed

# Create a meshgrid of longitude and latitude
lon_a, lat_a = np.meshgrid(longitude_a, latitude_a)

# Generate  altitude values for demonstration purposes
data_a = list(zip(lat_a.flatten(), lon_a.flatten(), values_a.flatten()))

# add to map layer
plugins.HeatMap(data_a, name='atlite',opacity=0.3).add_to(atlite_layer_heatmap)


########################################################################
## Bounding box
########################################################################
# add the bounding box user should stay within
# Get the maximum and minimum latitude and longitude values
max_latitude = atlite_capacity_factors_avg.latitude.max().values
min_latitude = atlite_capacity_factors_avg.latitude.min().values
max_longitude = atlite_capacity_factors_avg.longitude.max().values
min_longitude = atlite_capacity_factors_avg.longitude.min().values

# rectangle polygon
user_bound_frame = folium.Rectangle(
    bounds=[[min_latitude, min_longitude], [max_latitude, max_longitude]],
    color='blue',
    fill=False,
    weight=5,
    opacity=1.0,
    popup=folium.Popup('Put your points and polygons within this bounding box! Avoid masked values!', parse_html=True),  # Add a message to the rectangle
)
# south_africa_frame.add_to(m)
user_bound_frame.add_to(user_bound_layer_polygon)

########################################################################
## Wind Atlas PNG layer
########################################################################
# add the wind atlas capacity factor to the map
wind_atlas_capacity_factor_file = os.environ.get("WIND_ATLAS_CAPACITY_FACTORS_PNG_FILE_LOCATION")

# wind_file_params = [2381.93855019098555204, 0, 0, -2381.93855019098555204, 1079888.20687509560957551, -2294353.40437131375074387]
# Specify the geographical bounds of the PNG file
# left, bottom, right, top = 9.6,-35.8,37.8,-20.0
png_left, png_bottom, png_right, png_top = float(os.environ.get("WIND_ATLAS_PNG_LONGITUDE_LEFT")),\
                           float(os.environ.get("WIND_ATLAS_PNG_LATITUDE_BOTTOM")),\
                           float(os.environ.get("WIND_ATLAS_PNG_LONGITUDE_RIGHT")),\
                           float(os.environ.get("WIND_ATLAS_PNG_LATITUDE_TOP"))

# build layer
wind_atlas_png_overlay = folium.raster_layers.ImageOverlay(
    image=wind_atlas_capacity_factor_file,
    bounds = [[png_bottom, png_left], [png_top, png_right]],
    opacity=0.3,
    interactive=True,
    # mercator_project=True,  #errors if uncomment! Specify that the projection is mercator
    # wind_file_params=wind_file_params,
)
# image_overlay.add_to(m)
wind_atlas_png_overlay.add_to(wind_atlas_layer_png)

########################################################################
## Wind Atlas heatmap layer
########################################################################
# get down scaling resolution of wind atlas netcdf i.e. number of points to skip for lat lon values in array, to make things render faster
wind_atlas_resolution_reduction = int(os.environ.get("WIND_ATLAS_RESOLUTION_REDUCTION"))
# open wind atlas netcdf
wind_atlas_netcdf = xr.open_dataset(os.environ.get("WIND_ATLAS_CAPACITY_FACTORS_HEATMAP_FILE_LOCATION"))

# Select every wind_atlas_resolution_reduction latitude and longitude along with capacity_factor
capacity_factor_subset = wind_atlas_netcdf.sel(lat=wind_atlas_netcdf.lat.values[::wind_atlas_resolution_reduction], lon=wind_atlas_netcdf.lon.values[::wind_atlas_resolution_reduction])

# Access the capacity_factor variable from the subset
latitude_wa = capacity_factor_subset[os.environ.get("WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME")].values.astype(float)
longitude_wa = capacity_factor_subset[os.environ.get("WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME")].values.astype(float)
values_wa = capacity_factor_subset[os.environ.get("WIND_ATLAS_HEATMAP_DATA_VARIABLE_NAME")].values.astype(float)
values_wa[np.isnan(values_wa)] = 0.0  # Replace NaN with 0.0, you can choose a different value if needed
lon_wa, lat_wa = np.meshgrid(longitude_wa, latitude_wa)
# serialize data for folium
data_wa = list(zip(lat_wa.flatten(), lon_wa.flatten(), values_wa.flatten()))
# add to map layer
plugins.HeatMap(data_wa, name='atlas',opacity=0.3).add_to(wind_atlas_layer_heatmap)


########################################################################
## Mask layers
########################################################################
# add the mask layers to the map
mask_layers = support_functions.read_masks_as_folium_layers()




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
wind_atlas_layer_png.add_to(m)
wind_atlas_layer_heatmap.add_to(m)
atlite_layer_heatmap.add_to(m)
user_bound_layer_polygon.add_to(m)
for mask_layer in mask_layers:   # masks
    mask_layer.add_to(m)

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
            html.H1("Multiple tier per geometry option", style={'textAlign': 'center', 'color': 'white', 'background-color': 'lightgreen', 'padding': '20px'}),
            html.Ul([
                html.Li("1. Please select your geometries within the demarcated area. You may use polygons, points, rectangles or circles. Note circles are considered points. For point geometries, only one tier is returned."),
                html.Li("2. Ensure your geometries are within the bounding box of the Atlite data. Any geometry outside this box will be discarded."),
                html.Li("3. Click the export on the map to save a geojson file of the geometry."),
                html.Li("4. Copy the geojson file into the current working directory assets/user_geometry and set the environment varibale to the name of the geometry file. run the tier_generation script"),
                html.Li("5. Run the second step tier generation script."),
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
            html.Img(src=app.get_asset_url('static/csir_logo.jpg'), style={'width': '150px', 'height': 'auto', 'margin-right': '20px'}),
            html.Img(src=app.get_asset_url('static/leapre_logo.jpg'), style={'width': '150px', 'height': 'auto', 'margin-left': '20px'}),
        ],
        style={'bottom': 0, 'width': '95vw', 'padding': '20px', 'background-color': 'lightgray', 'text-align': 'center'}
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
