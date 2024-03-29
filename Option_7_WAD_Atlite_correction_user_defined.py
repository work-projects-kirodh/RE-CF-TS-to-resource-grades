"""
Purpose: Optional
    User defined function to autocorrect the Atlite time series with the wind atlas data
    Use at users own risk (untested)
"""
import os
from dotenv import load_dotenv
import argparse

################################
# system args section
################################
# used for running the codes
def parse_arguments():
    parser = argparse.ArgumentParser(description="(Option 1) Script to calculate average capacity factors.")
    parser.add_argument('--WIND_ATLAS_DATA', default=None, required=False, help="Wind Atlas data")
    parser.add_argument('--ATLITE_DATA', default=None, required=False, help="Atlite data.")

    # parse args
    args = parser.parse_args()

    # Check if all arguments are provided
    if all(arg is None for arg in vars(args).values()):
        raise ValueError("ERROR: All arguments are None!")

    # Check if any of the arguments are provided
    if any(arg is None for arg in vars(args).values()):
        print("Warning only some arguments provided! Code may fail.")

    return args


def load_from_env():
    # load data from .env file
    load_dotenv()
    env_vars =  {
        "WIND_ATLAS_DATA" : os.environ.get("WIND_ATLAS_DATA"),
        "ATLITE_DATA" : os.environ.get("ATLITE_DATA"),
    }
    # if None in env_vars.values():
    #     # raise ValueError("One or more environment variables are not set in the .env file.")
    #     print("WARNING: One or more environment variables are not set in the .env file!")

    # Store the names of variables that are None
    unset_variables = []

    for key, value in env_vars.items():
        if value is None:
            unset_variables.append(key)

    if unset_variables:
        print("WARNING: The following environment variables are not set in the .env file:")
        for var in unset_variables:
            print("...... -  ", var)

    return env_vars


################################################################
# main codes:

def wind_atlas_correction(WIND_ATLAS_DATA,ATLITE_DATA):
    # 1. read in current timeseries
    # 2. read in wind atlas data
    # 3. do correction
    # 4. save capacity factor timeseries
    pass

if __name__ == '__main__':
    # check args or load env file and run codes
    try:
        print("TRYING TO USE ARGUMENTS")
        args = parse_arguments()
        print("ARGUMENTS FOUND. USING ARGUMENTS")

        # RUN CODES
        wind_atlas_correction(**vars(args))
    except Exception as e:
        print("ARGUMENTS NOT FOUND: ",e)
        try:
            print("TRYING TO LOAD ENV FILE VARIABLES")
            # Load variables from the .env file
            args = load_from_env()
            print("ENV FILE FOUND. USING ENV FILE")

            # RUN CODES
            wind_atlas_correction(**args)

        except Exception as e:
            print("ENV FILE NOT FOUND: ",e)
            print("ERROR ... USER ARGS AND ENV FILE NOT FOUND, ABORTING!")
            raise ValueError("COULD NOT FIND ARGS OR LOAD ENV FILE. USER ARGS OR ENV FILE MISSING.")


    # args example use:
    # python Option_7_WAD_Atlite_correction_user_defined.py --WIND_ATLAS_DATA "path/to/WAD"  --ATLITE_DATA "path/to/Atlite/data"

