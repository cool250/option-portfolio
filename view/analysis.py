import dash_bootstrap_components as dbc
import dash_tabulator
from dash import dcc, html
from dash.dependencies import Input, Output, State

from app import app

TOP_COLUMN = dbc.Form(
    [
        dbc.Row(
            [
                dbc.Col(
                    children=[
                        dbc.Label("Choose one", size="sm"),
                        dbc.Select(
                            options=[
                                {"label": "SINGLE PUT", "value": "PUT"},
                                {"label": "SINGLE CALL", "value": "CALL"},
                                {"label": "VERTICAL PUT", "value": "V_PUT"},
                                {"label": "VERTICAL CALL", "value": "V_CALL"},
                            ],
                            value="",
                            id="a_contract_type",
                            placeholder="Select",
                            size="sm",
                        ),
                    ],
                    width=2,
                ),
                dbc.Col(
                    children=[
                        dbc.Label("Ticker", size="sm"),
                        dbc.Input(
                            type="text",
                            id="a_ticker",
                            placeholder="Enter Ticker",
                            size="sm",
                        ),
                    ],
                    width=2,
                ),
                dbc.Col(
                    children=[
                        dbc.Button(
                            "Search",
                            color="primary",
                            id="analysis-btn",
                            className="mt-4",
                        ),
                    ],
                    width=2,
                ),
            ],
        ),
    ],
)

SEARCH_RESULT = html.Div(id="a_content")

layout = dbc.Container(
    [
        dbc.Row(TOP_COLUMN),
        html.P(),
        dbc.Row(SEARCH_RESULT),
    ],
)


@app.callback(
    Output("a_content", "children"),
    [Input("analysis-btn", "n_clicks")],
    [
        State("a_contract_type", "value"),
        State("a_ticker", "value"),
    ],
)
def on_button_click(n, contract_type, ticker):
    return ""
