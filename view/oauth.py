import logging

import dash
import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output, State

from app import app
from broker.base import Base

layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.Label("URL"),
                ),

                dbc.Col(
                    dbc.Input(
                        type="text",
                        id="url_str",
                        placeholder="",
                    ),
                    width = 8
                ),
     
                dbc.Col(
                    dbc.Button(
                        "Enter",
                        color="primary",
                        className="float-right",
                        id="oauth-btn",
                    ),
                ),
            ]
        ),
        dbc.Row(
            dbc.Spinner(html.Div(id="success-message")),
        ),
     
    ]
)


@app.callback(
    Output("success-message", "children"),
    Input("oauth-btn", "n_clicks"),
    [
        State("url_str", "value"),
    ],
)
def on_button_click(n, url_str):
    if n is not None:
        base = Base()
        base.login(url_str)
    return ""
