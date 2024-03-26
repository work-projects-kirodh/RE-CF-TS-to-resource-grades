import os
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dotenv import load_dotenv

# Load variables from the .env file
load_dotenv()

# Function to format the file size to 2 decimal places
def format_file_size(file_size):
    return round(file_size, 2)

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

# Define a function to load CSV files, check for column 'tier_1', and plot if file size is <= 100 MB
def process_csv_files(folder_path):
    plots = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".csv"):
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                if file_size <= 100 * 1024 * 1024:  # 100 MB
                    df = pd.read_csv(file_path)
                    if 'tier_1' in df.columns:
                        fig = px.line(df, x=df.index, y=df.columns, title=f'File: {file}')
                        plots.append(dcc.Graph(figure=fig))
                else:
                    file_size_too_big.append({file:file_size/(1024 * 1024.0)})
    return plots

# Load CSV files and generate plots
plots  = process_csv_files(os.environ.get("OPTION_1_OUTPUT_FOLDER"))
plots += process_csv_files(os.environ.get("OPTION_2_OUTPUT_FOLDER"))
plots += process_csv_files(os.environ.get("OPTION_3_OUTPUT_FOLDER"))
plots += process_csv_files(os.environ.get("OPTION_4_OUTPUT_FOLDER"))
plots += process_csv_files(os.environ.get("OPTION_5_OUTPUT_FOLDER"))
plots += process_csv_files(os.environ.get("OPTION_6_OUTPUT_FOLDER"))

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


# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
