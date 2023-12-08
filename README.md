Tier selection and preprocessing toolbox for Irena-Flextool
=============================================================

This tool box consists of four Python scripts:
- step_1____.py prepares the capacity factor data from atlite. This will output an averaged over time capacity factor in the assets folder. This code will also find the top certain percentage capacity factor and average these to give you capacity factors you can use (option 1). 
- step_2____.py provides an interactive map interface on your browser which allows the user to select their tiers. A geojson file needs to be exported. using the export button.
- step_3____.py uses the atlite capacity factors and the designated points and polygons in the geojson file to extract the tiers of capacity factors. This will produce a csv file (option 2) with all the necessary tiers. The last method uses the tiers and allows the user to select the parts of each tier to create the final capacity factors they so wish (option 3).

Notes:
-------

- All relevant Python packages are found in requirements.txt (I may be missing some :-)) 
- Make sure to copy the sample.env to an .env file. This .env file, which contains all the user settings, is the user settings. Rather not change the assets folder. Keep that as is. The file names you can change as you need. Edit this file to configure the preprocessing scripts.
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
