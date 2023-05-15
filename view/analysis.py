import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_tabulator
from opstrat import multi_plotter
from broker.quotes import Quotes

import plotly.express as px

from app import app

TICKER_LOOKUP_ROW = dbc.Row(children=
        [
            dbc.Col(
                children=[
                    dbc.Label("TICKER", size="sm"),
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
                    html.Div(id="a_spot"),
                ],
                width=1,
            ),
            dbc.Col(
                children=[
                    dbc.Button(
                        "Lookup",
                        color="primary",
                        id="lookup-btn",
                        className="mt-4",
                    ),
                ],
                width=1,
            ),
        ],
    )

STRATEGY_ENTRY_ROW = dbc.Row(children=
        [
            dbc.Col(
                children=[
                    dbc.Label("Option Type", size="sm"),
                    dbc.Select(
                        options=[
                            {"label": "PUT", "value": "p"},
                            {"label": "CALL", "value": "c"},
                            {"label": "STOCK", "value": "e"},
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
        style=dict(display="none"),
        id="table_row",
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

STRATEGY_CHART = dbc.Row(id="graph_div")

layout = dbc.Container(
    [
        TICKER_LOOKUP_ROW,
        html.P(),
        STRATEGY_ENTRY_ROW,
        html.P(),
        STRATEGY_LIST,
        html.P(),
        STRATEGY_CHART,
        # dcc.Store stores the intermediate value
        dcc.Store(id="cache_data"),
        html.Div(id="hidden-div", style={"display": "none"}),
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
        State("a_premium", "value"),
        State("a_lot", "value"),
        State("a_strike", "value"),
        State("cache_data", "data"),
    ],
)
def on_add_click(n, op_type, tr_type, op_pr, contract, strike, cache_data):
    if n is None:
        return [], None, dict(display="none")
    else:
        contract_obj = {
            # "key": n,
            "op_type": op_type,
            "tr_type": tr_type,
            "op_pr": float(op_pr),
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
                rowDeleted=True,
            ),
        )
        return cache_obj, dt, dict()


@app.callback(
    Output("graph_div", "children"),
    [Input("analysis-btn", "n_clicks")],
    [
        State("cache_data", "data"),
        State("a_spot", "children"),
    ],
)
def on_analyze_click(n, cache_data, spot_price):
    if n is None:
        return None
    else:
        spot = float(spot_price)
        fig = multi_plotter(spot=spot, op_list=cache_data)
        return dcc.Graph(figure=fig)


@app.callback(
    Output("a_spot", "children"),
    Output("table_row", "style"),
    [Input("lookup-btn", "n_clicks")],
    [
        State("a_ticker", "value"),
    ],
)
def on_lookup_click(n, ticker):
    if n is None:
        return None, dict(display="none")
    else:
        quotes = Quotes()
        res = quotes.get_quotes(ticker)
        return res["mark"], dict()
