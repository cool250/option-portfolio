import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_tabulator
import plotly.graph_objects as go
from opstrat import multi_plotter
import numpy as np

from app import app

TOP_COLUMN = dbc.Form(
    [
        dbc.Row(
            [
                dbc.Col(
                    children=[
                        dbc.Label("Option Type", size="sm"),
                        dbc.Select(
                            options=[
                                {"label": "PUT", "value": "p"},
                                {"label": "CALL", "value": "c"},
                            ],
                            value="",
                            id="a_contractType",
                            placeholder="Select",
                            size="sm",
                        ),
                    ],
                    width=1,
                ),
                dbc.Col(
                    children=[
                        dbc.Label("Transaction", size="sm"),
                        dbc.Select(
                            options=[
                                {"label": "SELL", "value": "s"},
                                {"label": "BUY", "value": "b"},
                            ],
                            value="",
                            id="a_tran_type",
                            placeholder="Select",
                            size="sm",
                        ),
                    ],
                    width=1,
                ),
                dbc.Col(
                    children=[
                        dbc.Label("Ticker", size="sm"),
                        dbc.Input(
                            type="text",
                            id="a_ticker",
                            placeholder="",
                            size="sm",
                        ),
                    ],
                    width=1,
                ),
                dbc.Col(
                    children=[
                        dbc.Label("Premium", size="sm"),
                        dbc.Input(
                            type="text",
                            id="a_premium",
                            placeholder="",
                            size="sm",
                        ),
                    ],
                    width=1,
                ),
                dbc.Col(
                    children=[
                        dbc.Label("Strike", size="sm"),
                        dbc.Input(
                            type="text",
                            id="a_strike",
                            placeholder="",
                            size="sm",
                        ),
                    ],
                    width=1,
                ),
                   dbc.Col(
                    children=[
                        dbc.Label("Lot Size", size="sm"),
                        dbc.Input(
                            type="text",
                            id="a_lot",
                            placeholder="",
                            size="sm",
                        ),
                    ],
                    width=1,
                ),
                dbc.Col(
                    children=[
                        dbc.Button(
                            "Add",
                            color="primary",
                            id="add-btn",
                            className="mt-4",
                        ),
                    ],
                    width=1,
                ),
            ],
        ),
    ],
)

STRATEGY_LIST = dbc.Row(
    children=[
        dbc.Col(
            children=[
                html.Div(id="a_content"),
            ]
        ),
        dbc.Col(
            children=[
                dbc.Button(
                    "Analyze",
                    color="primary",
                    id="analysis-btn",
                    className="mt-4",
                    style=dict(display="none"),
                ),
            ]
        ),
    ]
)

STRATEGY_CHART = dbc.Row(
    children=[
        dcc.Graph(id="a_graph"),
    ]
)

layout = dbc.Container(
    [
        dbc.Row(TOP_COLUMN),
        html.P(),
        dbc.Row(STRATEGY_LIST),
        html.P(),
        dbc.Row(STRATEGY_CHART),
        # dcc.Store stores the intermediate value
        dcc.Store(id="cache_data"),
    ],
)


@app.callback(
    Output("cache_data", "data"),
    Output("a_content", "children"),
    Output("analysis-btn", "style"),
    [Input("add-btn", "n_clicks")],
    [
        State("a_contractType", "value"),
        State("a_tran_type", "value"),
        State("a_ticker", "value"),
        State("a_premium", "value"),
        State("a_lot", "value"),
        State("a_strike", "value"),
        State("cache_data", "data"),
    ],
)
def on_add_click(n, op_type, tr_type, ticker, op_pr, contract, strike, cache_data):
    if n is None:
        return [], None, dict(display="none")
    else:
        contract_obj = {
            "op_type": op_type,
            "tr_type": tr_type,
            "ticker": ticker,
            "op_pr": int(op_pr),
            "contract": int(contract),
            "strike": int(strike),
        }
        cache_obj = cache_data
        if not cache_obj:
            cache_obj = []
        cache_obj.append(contract_obj)
        # Display the strategies selected
        df = pd.DataFrame.from_dict(cache_obj)
        dt = (
            dash_tabulator.DashTabulator(
                id="analysis-table",
                columns=[{"id": i, "title": i, "field": i} for i in df.columns],
                data=df.to_dict("records"),
            ),
        )
        return cache_obj, dt, dict()


@app.callback(
    Output("a_graph", "figure"),
    [Input("analysis-btn", "n_clicks")],
    [
        State("cache_data", "data"),
    ],
)
def on_analyze_click(n, cache_data):
    if n is None:
        return None
    else:
        spot = 410
        # fig = multi_plotter(spot=spot, op_list=cache_data)
        op_1 = {'op_type':'c','strike':420,'tr_type':'s','op_pr':3.27}
        op_2 = {'op_type':'p','strike':400,'tr_type':'s','op_pr':3.02}
        op_3 = {'op_type':'c','strike':425,'tr_type':'b','op_pr':1.53}
        fig = multi_plotter(spot=412, op_list=[op_1,op_2, op_3])
        return fig
