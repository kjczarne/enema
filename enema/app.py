import dash
import dash_core_components as dcc
import dash_html_components as html
from dash_html_components.Button import Button
from dash_html_components.Label import Label
import plotly.express as px
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output, State
import dash_table as dtb
import dash_daq as daq
import sqlite3
import os
from pathlib import Path
from dataclasses import dataclass
from typing import ClassVar
import dash_auth
from enema.crypto import decrypt_password, KEY
from flask_restful import Api
from enema.data_model import (
    SubsystemStatusRoute, NodesRoute, StatusRoute, db_connection,
    read_table, Tables, update_status,
    get_joined_nodes_and_subsystems
)
from threading import Thread


# DATABASE =====================================================================



# run schema if the tables don't exist already:
with open(Path(os.path.dirname(__file__)) / "schema.sql", 'r') as f:
    schema_string = f.read()

db_connection().executescript(schema_string)

df_auth = read_table(Tables.auth)

# ==============================================================================


# BOILERPLATE ==================================================================

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

auth = dash_auth.BasicAuth(
    app,
    {
        k:v for k,v in zip(
            list(df_auth['user']), 
            [decrypt_password(p, KEY) for p in df_auth['password']]
        )
    }
)

app.config.suppress_callback_exceptions = True


@dataclass
class Defaults:
    bool_switch: ClassVar[bool] = False
    heading_style: ClassVar[dict] = {"text-align": "center"}
    link_style: ClassVar[dict] = {"text-align": "center", "font-size": "25px"}
    paragraph_style: ClassVar[dict] = {"text-align": "justify"}
    contact_info_style: ClassVar[dict] = {"text-align": "center"}
    centered_notice: ClassVar[dict] = {
        "text-align": "center",
        "font-weight": "bold"
    }
    centered_div: ClassVar[dict] = {
        "text-align": "center",
        "margin-left": "auto",
        "margin-right": "auto"
    }


data_table = lambda component_id, df: dtb.DataTable(
    id=component_id,
    columns=[{"name": i, "id": i} for i in df.columns],
    data=df.to_dict('records')
)

# ==============================================================================


# APP ==========================================================================
app.layout = html.Div(children=[
    dcc.Store('state-click-refresh'),
    dcc.Store('state-clicks-claim'),
    dcc.Store('state-clicks-release'),
    html.H1(
        id='main-title', 
        children="enema",
        style=Defaults.heading_style
    ),
    html.Div(
        id='main-container',
        children=[
            html.Button(
                id='load-button',
                children="Load/Refresh"
            ),
            html.Table(id='subsystems-table', style=Defaults.centered_div)
        ],
        style=Defaults.centered_div
    )
], style={"padding": "30px 60px 30px 60px"})


@app.callback(
    Output('subsystems-table', 'children'),
    Output('state-click-refresh', 'data'),
    Input('load-button', 'n_clicks'),
    State('state-click-refresh', 'data')
)
def on_load_subsystems(n_clicks, n_clicks_prev):
    df = get_joined_nodes_and_subsystems()
    rows = df.to_dict('records')
    is_busy, style = validate(subsystem_id)
    subsystem_records = [
        html.Tr(children=[
            html.Td(row['subsystem_name']),
            html.Td(row['node_name']),
            html.Td(
                id=str(row['subsystem_id'])+'-busy', 
                children=is_busy,
                style=style
            ),
            html.Td(
                html.Button(
                    id=str(row['subsystem_id'])+'-claim-button',
                    children="Claim"
                ),
            ),
            html.Td(
                html.Button(
                    id=str(row['subsystem_id'])+'-release-button',
                    children="Release"
                )
            )
        ], style=Defaults.centered_div) for row in rows
    ]
    if not n_clicks_prev:
        n_clicks_prev = 0
    if n_clicks:
        if n_clicks > n_clicks_prev:
            lst = [
                html.Tr(children=[
                    html.Th("Subsystem"),
                    html.Th("Node"),
                    html.Th("Busy?"),
                    html.Th("Claim"),
                    html.Th("Release")
                ], style=Defaults.centered_div)
            ] + subsystem_records
            return lst, n_clicks_prev
        n_clicks_prev = n_clicks
    return [], n_clicks_prev

# TODO: after this is done add notes on how to use `dcc.Store`


def validate(subsystem_id: int):
    df = get_joined_nodes_and_subsystems()
    validated = df.loc[subsystem_id]['is_busy']
    if validated == 1:
        return validated, {'background-color': 'red'}
    elif validated == 0:
        return validated, {'background-color': 'green'}
    else:
        return validated, {'background-color': 'grey'}


df = get_joined_nodes_and_subsystems()
for subsystem_id in df['subsystem_id']:
    @app.callback(
        Output(f'{subsystem_id}-busy', 'children'),
        Output(f'{subsystem_id}-busy', 'style'),
        Output('state-clicks-claim', 'data'),
        Output('state-clicks-release', 'data'),
        Input(f'{subsystem_id}-claim-button', 'n_clicks'),
        Input(f'{subsystem_id}-release-button', 'n_clicks'),
        State('state-clicks-claim', 'data'),
        State('state-clicks-release', 'data')
    )
    def on_claim(n_clicks_claim, n_clicks_release, n_clicks_prev_claim, n_clicks_prev_release):

        if not n_clicks_prev_claim:
            n_clicks_prev_claim = 0
        if not n_clicks_prev_release:
            n_clicks_prev_release = 0
        if n_clicks_claim:
            if n_clicks_claim > n_clicks_prev_claim:
                update_status(1, subsystem_id)
            n_clicks_prev_claim = n_clicks_claim
        if n_clicks_release:
            if n_clicks_release > n_clicks_prev_release:
                update_status(0, subsystem_id)
            n_clicks_prev_release = n_clicks_release
        return *validate(subsystem_id), n_clicks_prev_claim, n_clicks_prev_release


api = Api(app.server)

api.add_resource(StatusRoute, '/status')
api.add_resource(SubsystemStatusRoute, '/subsystem/status/<string:subsystem_id>')
api.add_resource(NodesRoute, '/nodes')

server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
