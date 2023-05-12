import dash_bootstrap_components as dbc
import json
from dash import dcc, html
from dash.dependencies import Input, Output, State

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
                                {"label": "PUT", "value": "PUT"},
                                {"label": "CALL", "value": "CALL"},
                            ],
                            value="",
                            id="a_contractType",
                            placeholder="Select",
                            size="sm",
                        ),
                    ],
                    width=2,
                ),
                dbc.Col(
                    children=[
                        dbc.Label("Transaction Type", size="sm"),
                        dbc.Select(
                            options=[
                                {"label": "SELL", "value": "SELL"},
                                {"label": "BUY", "value": "BUY"},
                            ],
                            value="",
                            id="a_tran_type",
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
                            "Add",
                            color="primary",
                            id="add-btn",
                            className="mt-4",
                        ),
                    ],
                    width=2,
                ),
                dbc.Col(
                    children=[
                        dbc.Button(
                            "Analyze",
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
        # dcc.Store stores the intermediate value
        dcc.Store(id='cache_data')
    ],
)


@app.callback(
    Output('cache_data', 'data'),
    [Input("add-btn", "n_clicks")],
    [
        State("a_contractType", "value"),
        State("a_tran_type", "value"),
        State("a_ticker", "value"),
        State('cache_data', 'data'),
    ],
)
def on_add_click(n, a_contractType, a_tran_type, ticker, cache_data):
    if n is None:
        return []
    else:
        contract_obj = {'a_contractType': a_contractType, 'a_tran_type': a_tran_type, 'ticker': ticker}
        cache_obj = cache_data
        if not cache_obj:
            cache_obj = []
        cache_obj.append(contract_obj)
        return cache_obj
    

@app.callback(
    Output('a_content', 'children'),
    [Input("analysis-btn", "n_clicks")],
    [
        State('cache_data', 'data'),
    ],
)
def on_analyze_click(n, cache_data):
    if n is None:
        return ""
    else:
        cache_obj = cache_data
        return cache_obj
    
