Tier selection and preprocessing toolbox for Irena-Flextool
=============================================================


Tier generation options available:
------------------------------------------------

There are different tier options available:
- Option 1 (dev complete): The user defines an upper percentage limit on the data e.g. I want the upper 10%. Using the averaged Atlite data, this option will find the top certain percentage capacity factors. The corresponding Atlite capacity factor timeseries data is saved as a separate tier. The last tier generated is the average of all the Atlite timeseries found in the upper user defined percentage.
- Option 2:(dev complete): This is the same as Option 1, except that the Wind Atlas data is used to find the location of the upper percentage tiers. Based on these locations, the closest locations in the Atlite data are then used for generating the tiers. 
- Option 3 (dev complete): There are 5 user defined tier bounds. Using the averaged Atlite data, this option will find the bounded percentage band capacity factors for each of those tiers. The timeseries Atlite capacity factor data for each tier bound is averaged in order to generate one timeseries per tier.
- Option 4: This is the same as Option 3, except that the tier bounds are generated from the Wind Atlas data. The locations are then closely matched to the Atlite data and the timeseries are then found. These are averaged to generate one timeseries per tier.
- Option 5: (Two scripts need to be run, geometry creation and tier generation). The user draws their own geometries to indicate tier boundaries. In each of these geometries the Atlite timeseries data is extracted and averaged. Thus giving one timeseries and tier per geometry.
- Option 6: (Two scripts need to be run, geometry creation and tier generation). This is the same as Option 5, except that for each geometry there are multiple tiers. These tiers are based on the tier bounds provided by the user. Note that for point geometries, only one tier is returned.
- Option 7: (User creates function). This function takes tiers and then calculates the new scaled tiers using the Wind Atlas data. The user must provide the function for this.


Scripts:
------------------------------------------------

This tool box consists of the following Python scripts:
- Option 1: Option_1_upper_percentage_atlite.py prepares the capacity factor data from atlite. This will output an averaged over time capacity factor in the assets folder. This code will also find the top certain percentage capacity factor and average these to give you capacity factors you can use (option 1). Option 1A is also bundled in this code and works on bounded tiers. In the .env file there are 5 tiers which the user can choose certain bounds. Dont need to do step 2 or 3 if you are running option 1 or 1A.  
- Option 2: Option_2_upper_percentage_WAD.py (optional, if you already have the geometries in geojson file, for option 2) provides an interactive map interface on your browser which allows the user to select their tiers. A geojson file needs to be exported. using the export button.
- Option 3: Option_3_bound_percentage_atlite.py uses the atlite capacity factors and the designated points and polygons in the geojson file to extract the tiers of capacity factors. This will produce a csv file (option 2) with all the necessary tiers. The last method uses the tiers and allows the user to select the parts of each tier to create the final capacity factors they so wish (option 3).
- Option 4: Option_4_bound_percentage_WAD.py (optional) provides a code stub for the user to correct the Atlite data using
- Option 5: Option_5_step1_geometry_selection.py and Option_5_step2_tier_generation_average_per_geometry.py
- Option 6: Option_6_step1_geometry_selection.py and Option_6_step2_tier_generation_bounds_per_geometry.py
- Option 7: Option_7_WAD_Atlite_correction_user_defined.py

Additionally, there are the Option_Support_Functions.py which are needed for some scripts to run.


Parameters and files that need to be set before running scripts:
--------------------------------------------------------------------

Parameters and variables can be set in the .env file. Or via the command line interface

- Option 1: var1 etc.
- Option 2: var2 etc.
- Option 3: var3 etc.
- Option 4: var4 etc.
- Option 5: var5 etc.
- Option 6: var6 etc.
- Option 7: var6 etc.


Viewing all tiers
-------------------

You can run the view_all_tiers.py script to show all the tiers of all the Options that were generated. These tiers are shown ona web browser interactive graph page.


Notes:
-------

- Option 1, 2,3 and 4 (and 7) dont require user input on a browser. Options 5 and 6 require the user input on a browser.
- All relevant Python packages are found in requirements.txt (I may be missing some :-)) 
- Make sure to copy the sample.env to an .env file. This .env file, which contains all the user settings, is the user settings. Rather not change the assets folder. Keep that as is. The file names you can change as you need. Edit this file to configure the preprocessing scripts.
- Too high a resolution is not a good idea for the world atlas netcdf data, this will significantly increase the rendering time.
- Only single band (not classified) .tif files used as masks, make sure they each have an extent. You can add as many as you want in the masks folder. A method is described in this readme on how to convert a classified raster to a single band raster.
- Please give step 1 for Option 5 and 6 some time before loading the map on the browser, it can takea while to read in the mask files



World Atlas Data preprep
---------------------------

- To get the png pic that works, use qgis, style the map accordingly, and click project then import/export then export map to image.
- Play with the bounds for the image (found in the .env file) so that it fits on the south african boarder.
- User can then select the tiers according to the world atlas capacity factors if they so wish.
- To obtain the netcdf file, use qgis to save the tiff as a netcdf file.


Masks preparation
------------------

As noted, only single band (not classified) .tif files used as masks, make sure they each have an extent. You can add as many as you want in the masks folder. A method is described in this readme on how to convert a classified raster to a single band raster.

If you have a classified tiff file and want to convert it to a single band then you can use QGIS.

![Classified vs Single Band tiff file](assets/static/classified_and_single_band_raster.PNG)


- Open QGIS and load the classified tiff layer
- Open the raster calculater (raster --> raster calculator) and perform the calculation "classified_raster_band@1" * 1.
- Save it into a new tiff file
- Use this new singleband tiff file as your mask in the assets/masks folder

![How to convert from Classified to Single Band tiff file](assets/static/convert_classified_to_single_band_raster.PNG)

Please remove all classified masks (or rename the extension) from the assets/masks folder so that it doesnt load them, this is to save you some run time.

Assumptions
-------------------

- For points geometry selection, the nearest timeseries datapoint is found and selected

Authors:
---------
- Kirodh Boodhraj
