import os
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dotenv import load_dotenv
import argparse

################################
# system args section
################################
# used for running the codes
def parse_arguments():
    parser = argparse.ArgumentParser(description="(View all tiers) Script to plot all tiers in all options.")
    parser.add_argument('--OPTION_1_OUTPUT_FOLDER', default=None, required=False, help="Output folder for Option 1 tiers.")
    parser.add_argument('--OPTION_2_OUTPUT_FOLDER', default=None, required=False, help="Output folder for Option 2 tiers.")
    parser.add_argument('--OPTION_3_OUTPUT_FOLDER', default=None, required=False, help="Output folder for Option 3 tiers.")
    parser.add_argument('--OPTION_4_OUTPUT_FOLDER', default=None, required=False, help="Output folder for Option 4 tiers.")
    parser.add_argument('--OPTION_5_OUTPUT_FOLDER', default=None, required=False, help="Output folder for Option 5 tiers.")
    parser.add_argument('--OPTION_6_OUTPUT_FOLDER', default=None, required=False, help="Output folder for Option 6 tiers.")

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
        "OPTION_1_OUTPUT_FOLDER" : os.environ.get("OPTION_1_OUTPUT_FOLDER"),
        "OPTION_2_OUTPUT_FOLDER" : os.environ.get("OPTION_2_OUTPUT_FOLDER"),
        "OPTION_3_OUTPUT_FOLDER" : os.environ.get("OPTION_3_OUTPUT_FOLDER"),
        "OPTION_4_OUTPUT_FOLDER" : os.environ.get("OPTION_4_OUTPUT_FOLDER"),
        "OPTION_5_OUTPUT_FOLDER" : os.environ.get("OPTION_5_OUTPUT_FOLDER"),
        "OPTION_6_OUTPUT_FOLDER" : os.environ.get("OPTION_6_OUTPUT_FOLDER"),
    }

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

# Function to format the file size to 2 decimal places
def format_file_size(file_size):
    return round(file_size, 2)

# Define a function to load CSV files, check for column 'tier_1', and plot if file size is <= 100 MB
def process_csv_files(folder_path,file_size_too_big):
    plots = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".csv"):
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                if file_size <= 50 * 1024 * 1024:  # 50 MB
                    df = pd.read_csv(file_path)
                    if 'tier_1' in df.columns:
                        fig = px.line(df, x=df.index, y=df.columns, title=f'File: {file}')
                        plots.append(dcc.Graph(figure=fig))
                else:
                    file_size_too_big.append({file:file_size/(1024 * 1024.0)})
    return plots


###################
# main function to run the plotting codes
def plot_all_tiers(OPTION_1_OUTPUT_FOLDER, OPTION_2_OUTPUT_FOLDER, OPTION_3_OUTPUT_FOLDER, OPTION_4_OUTPUT_FOLDER, OPTION_5_OUTPUT_FOLDER, OPTION_6_OUTPUT_FOLDER):
    # Create a Dash app
    app = dash.Dash(__name__)

    file_size_too_big = []


    # Define the layout of the app
    app.layout = html.Div([
        html.H1("CSV Data Plots"),
        html.Table(id="table",children = [
            html.Thead(html.Tr([
                html.Th("File Too Big For Display"),
                html.Th("File Size (Mb)")
            ])),
            html.Tbody([
                html.Tr([
                    html.Td(file_name),
                    html.Td(format_file_size(file_size))
                ]) for entry in file_size_too_big for file_name, file_size in entry.items()
            ])
        ], style={'margin': 'auto', 'border': '1px solid black', 'border-collapse': 'collapse'},),
        html.Div(id='graph-container', children=[
            dcc.Loading(
                id="loading-1",
                children=[html.Div(id="loading-output-1")]
            )
        ])
    ])


    # Load CSV files and generate plots
    plots  = process_csv_files(OPTION_1_OUTPUT_FOLDER,file_size_too_big)
    plots += process_csv_files(OPTION_2_OUTPUT_FOLDER,file_size_too_big)
    plots += process_csv_files(OPTION_3_OUTPUT_FOLDER,file_size_too_big)
    plots += process_csv_files(OPTION_4_OUTPUT_FOLDER,file_size_too_big)
    plots += process_csv_files(OPTION_5_OUTPUT_FOLDER,file_size_too_big)
    plots += process_csv_files(OPTION_6_OUTPUT_FOLDER,file_size_too_big)

    # Update the graph container with the generated plots
    app.layout['graph-container'].children = plots
    app.layout['table'].children = [html.Thead(html.Tr([
                html.Th("File Too Big For Display", style={'padding': '10px', 'border-right': '1px solid black'}),
                html.Th("File Size (Mb)", style={'padding': '10px', 'border-right': '1px solid black'}),
            ], style={'background-color': 'lightgray'})),
            html.Tbody([
                html.Tr([
                    html.Td(file_name, style={'padding': '10px', 'border-right': '1px solid black'}),
                    html.Td(format_file_size(file_size), style={'padding': '10px', 'border-right': '1px solid black'})
                ],style={'background-color': 'white' if i % 2 == 0 else 'lightgray'}) for i,entry in enumerate(file_size_too_big) for file_name, file_size in entry.items()
            ])]

    app.run_server(debug=True)


# Run the Dash app
if __name__ == '__main__':
    # check args or load env file and run codes
    print("Starting plotting for all options present ...")

    try:
        print("TRYING TO USE ARGUMENTS")
        args = parse_arguments()
        print("ARGUMENTS FOUND. USING ARGUMENTS")

        # RUN CODES
        plot_all_tiers(**vars(args))
    except Exception as e:
        print("ARGUMENTS NOT FOUND: ", e)
        try:
            print("TRYING TO LOAD ENV FILE VARIABLES")
            # Load variables from the .env file
            args = load_from_env()
            print("ENV FILE FOUND. USING ENV FILE")

            # RUN CODES
            plot_all_tiers(**args)

        except Exception as e:
            print("ENV FILE NOT FOUND: ", e)
            print("ERROR ... USER ARGS AND ENV FILE NOT FOUND, ABORTING!")
            raise ValueError("COULD NOT FIND ARGS OR LOAD ENV FILE. USER ARGS OR ENV FILE MISSING.")

    # args example use:
    # python View_all_tiers.py --OPTION_1_OUTPUT_FOLDER "assets/option_1_output" --OPTION_2_OUTPUT_FOLDER "assets/option_2_output"  --OPTION_3_OUTPUT_FOLDER "assets/option_3_output"  --OPTION_4_OUTPUT_FOLDER "assets/option_4_output"  --OPTION_5_OUTPUT_FOLDER "assets/option_5_output"  --OPTION_6_OUTPUT_FOLDER "assets/option_6_output"


