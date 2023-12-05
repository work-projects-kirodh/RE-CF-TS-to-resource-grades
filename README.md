Tier selection and preprocessing toolbox for Irena-Flextool
=============================================================

This tool box consists of four Python scripts:
- step_1____.py prepares the capacity factor data from atlite. This will output an averaged over time capacity factor in the assets folder.
- step_2____.py provides an interactive map interface on your browser which allows the user to select their tiers. A geojson file needs to be exported.
- step_3____.py uses the atlite capacity factors and the designated points and polygons in the geojson file to extract the tiers of capacity factors. This will produce a pandas dataframe with all the necessary tiers.
- step_4____.py uses the tiers and allows the user to select the parts of each tier to create the final capacity factors for the technology. 

Notes:
-------

- There is a .env file which contains all the user settings. Edit this file to configure the preprocessing scripts.
- Too high a resolution is not a good idea for the world atlas netcdf data, this will significantly increase the rendering time.


World Atlas Data preprep
---------------------------

- To get the png pic that works, use qgis, style the map accordingly, and click project then import/export then export map to image.
- Play with the bounds for the image (found in the .env file) so that it fits on the south african boarder.
- User can then select the tiers according to the world atlas capacity factors if they so wish.
- To obtain the netcdf file, use qgis to save the tiff as a netcdf file.


Authors:
---------
- Kirodh Boodhraj
