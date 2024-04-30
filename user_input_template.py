from Option_1_upper_percentage_atlite import average_capacity_factors_atlite as option_1
from Option_2_upper_percentage_WAD import average_capacity_factors_WAD as option_2
from Option_3_bound_percentage_atlite import average_capacity_factors_atlite as option_3
from Option_4_bound_percentage_WAD import average_bounded_capacity_factors_WAD as option_4
from Option_5_step1_geometry_selection import geometry_selection as option_5_step_1
from Option_5_step2_tier_generation_average_per_geometry import option_5_process_geometries_into_tiers as option_5_step_2
from Option_6_step1_geometry_selection import geometry_selection as option_6_step_1
from Option_6_step2_tier_generation_bounds_per_geometry import option_6_process_geometries_into_tiers as option_6_step_2
from Option_7_WAD_Atlite_correction_user_defined import wind_atlas_correction as option_7


# User inputs start
#------------------

# Option to run (1,2,3,4,5_1,5_2,6_1,6_2,7), note that for option 5 and 6, there are two steps
OPTION='5_1'

# Support Functions (Options 1, 2, 3, 4, 5, 6)
#-------------------------
# Real atlite data
#-------------------------
# put list of folders here for Atlite output data, comma separated list
ATLITE_CAPACITY_FACTORS_FOLDERS="atlite_output_data\output_month_1_Jan_2023\hourly_capacity_factors,atlite_output_data\output_month_2_Jan_2023\hourly_capacity_factors,atlite_output_data\output_month_3_Jan_2023\hourly_capacity_factors,atlite_output_data\output_month_4_Jan_2023\hourly_capacity_factors,atlite_output_data\output_month_5_Jan_2023\hourly_capacity_factors,atlite_output_data\output_month_6_Jan_2023\hourly_capacity_factors,atlite_output_data\output_month_7_Jan_2023\hourly_capacity_factors,atlite_output_data\output_month_8_Jan_2023\hourly_capacity_factors,atlite_output_data\output_month_9_Jan_2023\hourly_capacity_factors,atlite_output_data\output_month_10_Jan_2023\hourly_capacity_factors,atlite_output_data\output_month_11_Jan_2023\hourly_capacity_factors,atlite_output_data\output_month_12_Jan_2023\hourly_capacity_factors"
#-------------------------
# for the dummy data option
#-------------------------
ATLITE_DUMMY_DATA='False'        # if true then won't use real data
DUMMY_START_DATE='2023-01-01'
DUMMY_END_DATE='2024-01-01'
DUMMY_LATITUDE_TOP='-30.0'
DUMMY_LATITUDE_BOTTOM='-32.0'
DUMMY_LONGITUDE_LEFT='26.0'
DUMMY_LONGITUDE_RIGHT='28.0'
#-------------------------
# full capacity factors data
DATA_VARIABLE_NAME='capacity_factors'
TIME_VARIABLE_NAME='time'
#-------------------------
# store averaged capacity factors here, note it should be in the assets folder because otherwise it wont be recognized
AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION="assets/avg_atlite_capacity_factors.nc"
# variable names in the avg file
AVG_ATLITE_LATITUDE_VARIABLE_NAME='latitude'
AVG_ATLITE_LONGITUDE_VARIABLE_NAME='longitude'
AVG_ATLITE_DATA_VARIABLE_NAME='capacity_factors'


# Support Functions (Options 2, 4, 5, 6)
# wind atlas capacity factors
#----------------------------
# a good resolution is between 12 and 20?, make sure it is integer
WIND_ATLAS_RESOLUTION_REDUCTION='15'
WIND_ATLAS_CAPACITY_FACTORS_HEATMAP_FILE_LOCATION="assets/wind_atlas_capacity_factors.nc"
# variable names within netcdf file:
WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME='lat'
WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME='lon'
WIND_ATLAS_HEATMAP_DATA_VARIABLE_NAME='Band1'
REDUCED_WAD='True' #Warning, will take a very long time if not reduced  Option 2 and 4!


# Support Functions (Options 5, 6)
# Masks file for geometry selection (please add tiff files only)
#----------------------------
MASKS_FOLDER="assets/masks"


# technology and capacity scaling (Option 1,2,3,4,5,6)
#-----------
SCALE_CAPACITY_FACTORS='True'
MAXIMUM_CAPACITY='50' # MW



# global wind atlas capacity factors PNG (Options 5, 6)
#---------------------------------
# for visualization purposes
WIND_ATLAS_CAPACITY_FACTORS_PNG_FILE_LOCATION="assets/wind_atlas_capacity_factors.png"
# play around until you get good accurate coverage
WIND_ATLAS_PNG_LATITUDE_TOP='-20.0'
WIND_ATLAS_PNG_LATITUDE_BOTTOM='-35.8'
WIND_ATLAS_PNG_LONGITUDE_LEFT='9.6'
WIND_ATLAS_PNG_LONGITUDE_RIGHT='37.8'


# bounded tiers (Options 3, 4, 6)
#----------------------------------
PERCENT_UPPER_TIER1_CAPACITY_FACTORS='0,10'  # used for option 3, the above parameters are used for second option for tiers
PERCENT_UPPER_TIER2_CAPACITY_FACTORS='10,20'
PERCENT_UPPER_TIER3_CAPACITY_FACTORS='0,40'
PERCENT_UPPER_TIER4_CAPACITY_FACTORS='60,100'
PERCENT_UPPER_TIER5_CAPACITY_FACTORS='40,60'


# Option 1 variables:
#------------------
OPTION_1_OUTPUT_FOLDER="assets/option_1_output"
PERCENT_UPPER_CAPACITY_FACTORS_1='10'  # used for option 1, the above parameters are used for second option for tiers
# file locations option 1
PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE_1="option_1_top_percentage_locations.csv"
PERCENT_UPPER_CAPACITY_FACTORS_TIME_SERIES_FILE_1="option_1_top_percentage_capacity_factor_time_series.csv"

# Option 2 variables:
#------------------
OPTION_2_OUTPUT_FOLDER="assets/option_2_output"
PERCENT_UPPER_CAPACITY_FACTORS_2='10'
# file locations option 2
PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE_WAD_2="option_2_top_percentage_locations_wad.csv"
PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE_ATLITE_2="option_2_top_percentage_locations_atlite.csv"
PERCENT_UPPER_CAPACITY_FACTORS_TIME_SERIES_FILE_2="option_2_top_percentage_capacity_factor_time_series.csv"


# Option 3 variables:
#------------------
OPTION_3_OUTPUT_FOLDER="assets/option_3_output"
# Provide ranges in the format of lower,upper percentages for the tiers below. e.g. 0,10 is upper 10 percent
# output file locations option 3
BOUND_CAPACITY_FACTORS_TIME_SERIES_FILE_3="option_3_top_percentage_capacity_factor_time_series.csv"


# Option 4 variables:
#------------------
OPTION_4_OUTPUT_FOLDER="assets/option_4_output"
BOUND_CAPACITY_FACTORS_TIME_SERIES_FILE_4="option_4_bounded_percentage_capacity_factor_time_series.csv"

# Option 5 variables:
#------------------
OPTION_5_OUTPUT_FOLDER="assets/option_5_output"
OPTION_5_USER_GEOMETRIES_GEOJSON_FILE="assets/user_geometry/real_atlite.geojson"   #example.geojson"
OPTION_5_OUTPUT_TIERS_FILE="option_5_single_tiers_per_geometry.csv"
OPTION_5_GEOMETRY_REFERENCE_FILE="option_5_geometry_reference_file.csv"
OPTION_5_VIEW_VALID_GEOMETRIES='True'

# Option 6 variables:
#------------------
OPTION_6_OUTPUT_FOLDER="assets/option_6_output"
OPTION_6_USER_GEOMETRIES_GEOJSON_FILE="assets/user_geometry/real_atlite.geojson"   #example2.geojson"
OPTION_6_OUTPUT_TIERS_FILE="option_6_multiple_tiers_per_geometry.csv"
OPTION_6_GEOMETRY_REFERENCE_FILE="option_6_geometry_reference_file.csv"
OPTION_6_VIEW_VALID_GEOMETRIES='True'

# Option 7 variables: (user defined functions)
#------------------
OPTION_7_OUTPUT_FOLDER="assets/option_7_output"

# User inputs ends.
#------------------


# no user input below
if __name__ == '__main__':
    if OPTION == '1':
        option_1(ATLITE_DUMMY_DATA, ATLITE_CAPACITY_FACTORS_FOLDERS, DUMMY_START_DATE,
                                    DUMMY_END_DATE, DUMMY_LATITUDE_BOTTOM, DUMMY_LATITUDE_TOP, DUMMY_LONGITUDE_LEFT,
                                    DUMMY_LONGITUDE_RIGHT, MAXIMUM_CAPACITY, DATA_VARIABLE_NAME, TIME_VARIABLE_NAME,
                                    AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION, AVG_ATLITE_LATITUDE_VARIABLE_NAME,
                                    AVG_ATLITE_LONGITUDE_VARIABLE_NAME, PERCENT_UPPER_CAPACITY_FACTORS_1,
                                    OPTION_1_OUTPUT_FOLDER, PERCENT_UPPER_CAPACITY_FACTORS_TIME_SERIES_FILE_1,
                                    PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE_1, SCALE_CAPACITY_FACTORS)
    elif OPTION == '2':
        option_2(ATLITE_DUMMY_DATA, ATLITE_CAPACITY_FACTORS_FOLDERS, DUMMY_START_DATE,
                                     DUMMY_END_DATE, DUMMY_LATITUDE_BOTTOM, DUMMY_LATITUDE_TOP, DUMMY_LONGITUDE_LEFT,
                                     DUMMY_LONGITUDE_RIGHT, MAXIMUM_CAPACITY, DATA_VARIABLE_NAME, TIME_VARIABLE_NAME,
                                     AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION, AVG_ATLITE_LATITUDE_VARIABLE_NAME,
                                     AVG_ATLITE_LONGITUDE_VARIABLE_NAME, REDUCED_WAD, WIND_ATLAS_RESOLUTION_REDUCTION,
                                     WIND_ATLAS_CAPACITY_FACTORS_HEATMAP_FILE_LOCATION,
                                     WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME,
                                     WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME, WIND_ATLAS_HEATMAP_DATA_VARIABLE_NAME,
                                     PERCENT_UPPER_CAPACITY_FACTORS_2, OPTION_2_OUTPUT_FOLDER, SCALE_CAPACITY_FACTORS,
                                     PERCENT_UPPER_CAPACITY_FACTORS_TIME_SERIES_FILE_2,
                                     PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE_WAD_2,
                                     PERCENT_UPPER_CAPACITY_FACTORS_LOCATION_FILE_ATLITE_2)
    elif OPTION == '3':
        option_3(ATLITE_DUMMY_DATA, ATLITE_CAPACITY_FACTORS_FOLDERS, DUMMY_START_DATE,
                                        DUMMY_END_DATE, DUMMY_LATITUDE_BOTTOM, DUMMY_LATITUDE_TOP, DUMMY_LONGITUDE_LEFT,
                                        DUMMY_LONGITUDE_RIGHT, DATA_VARIABLE_NAME, TIME_VARIABLE_NAME,
                                        AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION, PERCENT_UPPER_TIER1_CAPACITY_FACTORS,
                                        PERCENT_UPPER_TIER2_CAPACITY_FACTORS, PERCENT_UPPER_TIER3_CAPACITY_FACTORS,
                                        PERCENT_UPPER_TIER4_CAPACITY_FACTORS, PERCENT_UPPER_TIER5_CAPACITY_FACTORS,
                                        AVG_ATLITE_LATITUDE_VARIABLE_NAME, AVG_ATLITE_LONGITUDE_VARIABLE_NAME,
                                        OPTION_3_OUTPUT_FOLDER, MAXIMUM_CAPACITY,
                                        BOUND_CAPACITY_FACTORS_TIME_SERIES_FILE_3, SCALE_CAPACITY_FACTORS)
    elif OPTION == '4':
        option_4(ATLITE_DUMMY_DATA, ATLITE_CAPACITY_FACTORS_FOLDERS, DUMMY_START_DATE,
                                             DUMMY_END_DATE, DUMMY_LATITUDE_BOTTOM, DUMMY_LATITUDE_TOP,
                                             DUMMY_LONGITUDE_LEFT, DUMMY_LONGITUDE_RIGHT, MAXIMUM_CAPACITY,
                                             DATA_VARIABLE_NAME, TIME_VARIABLE_NAME,
                                             AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION,
                                             AVG_ATLITE_LATITUDE_VARIABLE_NAME, AVG_ATLITE_LONGITUDE_VARIABLE_NAME,
                                             REDUCED_WAD, WIND_ATLAS_RESOLUTION_REDUCTION,
                                             WIND_ATLAS_CAPACITY_FACTORS_HEATMAP_FILE_LOCATION,
                                             WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME,
                                             WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME,
                                             WIND_ATLAS_HEATMAP_DATA_VARIABLE_NAME,
                                             PERCENT_UPPER_TIER1_CAPACITY_FACTORS, PERCENT_UPPER_TIER2_CAPACITY_FACTORS,
                                             PERCENT_UPPER_TIER3_CAPACITY_FACTORS, PERCENT_UPPER_TIER4_CAPACITY_FACTORS,
                                             PERCENT_UPPER_TIER5_CAPACITY_FACTORS, AVG_ATLITE_DATA_VARIABLE_NAME,
                                             OPTION_4_OUTPUT_FOLDER, SCALE_CAPACITY_FACTORS,
                                             BOUND_CAPACITY_FACTORS_TIME_SERIES_FILE_4)
    elif OPTION == '5_1':
        option_5_step_1(ATLITE_DUMMY_DATA, ATLITE_CAPACITY_FACTORS_FOLDERS, DUMMY_START_DATE, DUMMY_END_DATE,
                           DUMMY_LATITUDE_BOTTOM, DUMMY_LATITUDE_TOP, DUMMY_LONGITUDE_LEFT, DUMMY_LONGITUDE_RIGHT,
                           MAXIMUM_CAPACITY, DATA_VARIABLE_NAME, TIME_VARIABLE_NAME,
                           AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION, AVG_ATLITE_LATITUDE_VARIABLE_NAME,
                           AVG_ATLITE_LONGITUDE_VARIABLE_NAME, WIND_ATLAS_CAPACITY_FACTORS_PNG_FILE_LOCATION,
                           WIND_ATLAS_PNG_LONGITUDE_LEFT, WIND_ATLAS_PNG_LATITUDE_BOTTOM,
                           WIND_ATLAS_PNG_LONGITUDE_RIGHT, WIND_ATLAS_PNG_LATITUDE_TOP, WIND_ATLAS_RESOLUTION_REDUCTION,
                           WIND_ATLAS_CAPACITY_FACTORS_HEATMAP_FILE_LOCATION, WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME,
                           WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME, WIND_ATLAS_HEATMAP_DATA_VARIABLE_NAME,
                           MASKS_FOLDER)
    elif OPTION == '5_2':
        option_5_step_2(ATLITE_CAPACITY_FACTORS_FOLDERS, AVG_ATLITE_LONGITUDE_VARIABLE_NAME,
                                               AVG_ATLITE_LATITUDE_VARIABLE_NAME, AVG_ATLITE_DATA_VARIABLE_NAME,
                                               OPTION_5_USER_GEOMETRIES_GEOJSON_FILE, ATLITE_DUMMY_DATA,
                                               DUMMY_START_DATE, DUMMY_END_DATE, DUMMY_LATITUDE_BOTTOM,
                                               DUMMY_LATITUDE_TOP, DUMMY_LONGITUDE_LEFT, DUMMY_LONGITUDE_RIGHT,
                                               MAXIMUM_CAPACITY, DATA_VARIABLE_NAME, TIME_VARIABLE_NAME,
                                               AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION, OPTION_5_OUTPUT_FOLDER,
                                               SCALE_CAPACITY_FACTORS, OPTION_5_OUTPUT_TIERS_FILE,
                                               OPTION_5_GEOMETRY_REFERENCE_FILE, OPTION_5_VIEW_VALID_GEOMETRIES)
    elif OPTION == '6_1':
        option_6_step_1(ATLITE_DUMMY_DATA, ATLITE_CAPACITY_FACTORS_FOLDERS, DUMMY_START_DATE, DUMMY_END_DATE,
                           DUMMY_LATITUDE_BOTTOM, DUMMY_LATITUDE_TOP, DUMMY_LONGITUDE_LEFT, DUMMY_LONGITUDE_RIGHT,
                           MAXIMUM_CAPACITY, DATA_VARIABLE_NAME, TIME_VARIABLE_NAME,
                           AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION, AVG_ATLITE_LATITUDE_VARIABLE_NAME,
                           AVG_ATLITE_LONGITUDE_VARIABLE_NAME, WIND_ATLAS_CAPACITY_FACTORS_PNG_FILE_LOCATION,
                           WIND_ATLAS_PNG_LONGITUDE_LEFT, WIND_ATLAS_PNG_LATITUDE_BOTTOM,
                           WIND_ATLAS_PNG_LONGITUDE_RIGHT, WIND_ATLAS_PNG_LATITUDE_TOP, WIND_ATLAS_RESOLUTION_REDUCTION,
                           WIND_ATLAS_CAPACITY_FACTORS_HEATMAP_FILE_LOCATION, WIND_ATLAS_HEATMAP_LATITUDE_VARIABLE_NAME,
                           WIND_ATLAS_HEATMAP_LONGITUDE_VARIABLE_NAME, WIND_ATLAS_HEATMAP_DATA_VARIABLE_NAME,
                           MASKS_FOLDER)
    elif OPTION == '6_2':
        option_6_step_2(ATLITE_CAPACITY_FACTORS_FOLDERS, AVG_ATLITE_LONGITUDE_VARIABLE_NAME,
                                               AVG_ATLITE_LATITUDE_VARIABLE_NAME, AVG_ATLITE_DATA_VARIABLE_NAME,
                                               PERCENT_UPPER_TIER1_CAPACITY_FACTORS,
                                               PERCENT_UPPER_TIER2_CAPACITY_FACTORS,
                                               PERCENT_UPPER_TIER3_CAPACITY_FACTORS,
                                               PERCENT_UPPER_TIER4_CAPACITY_FACTORS,
                                               PERCENT_UPPER_TIER5_CAPACITY_FACTORS, DATA_VARIABLE_NAME,
                                               OPTION_6_USER_GEOMETRIES_GEOJSON_FILE, OPTION_6_OUTPUT_FOLDER,
                                               ATLITE_DUMMY_DATA, DUMMY_START_DATE, DUMMY_END_DATE,
                                               DUMMY_LATITUDE_BOTTOM, DUMMY_LATITUDE_TOP, DUMMY_LONGITUDE_LEFT,
                                               DUMMY_LONGITUDE_RIGHT, MAXIMUM_CAPACITY, TIME_VARIABLE_NAME,
                                               AVG_ATLITE_CAPACITY_FACTORS_FILE_LOCATION, SCALE_CAPACITY_FACTORS,
                                               OPTION_6_OUTPUT_TIERS_FILE, OPTION_6_GEOMETRY_REFERENCE_FILE,
                                               OPTION_6_VIEW_VALID_GEOMETRIES)
    elif OPTION == '7':
        option_7(WIND_ATLAS_CAPACITY_FACTORS_HEATMAP_FILE_LOCATION, ATLITE_CAPACITY_FACTORS_FOLDERS)
    else:
        print("WARNING: Unknown option: ",OPTION, ". Available options are 1,2,3,4,51,52,61,62,7")





