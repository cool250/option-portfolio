import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_tabulator
from opstrat import multi_plotter
from service import option_analysis


from app import app, cache
from utils.functions import formatter_number_2_digits

TICKER_LOOKUP_ROW = dbc.Row(
    children=[
        dbc.Col(
            children=[
                dbc.Label("TICKER"),
            ],
            width=2,
        ),
        dbc.Col(
            children=[
                dbc.Input(
                    type="text",
                    id="a_ticker",
                    placeholder="",
                    size="sm",
                ),
            ],
            width=2,
        ),
        dbc.Col(
            children=[
                html.Div(id="a_spot"),
            ],
            width=2,
        ),
        dbc.Col(
            children=[
                dbc.Label("Weeks", size="sm"),
            ],
            width=2,
        ),
        dbc.Col(
            children=[
                dbc.Select(
                    value="",
                    id="a_weeks",
                    placeholder="Select",
                    size="sm",
                ),
            ],
            width=2,
        ),
        dbc.Col(
            children=[
                dbc.Button(
                    "Lookup",
                    color="primary",
                    id="lookup-btn",
                    size="md",
                ),
            ],
            width=2,
        ),
    ],
    className="mt-4",
)

STRATEGY_ENTRY_ROW = dbc.Row(
    children=[
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
            width=2,
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
            width=2,
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
            width=2,
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
            width=2,
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
            width=2,
        ),
        dbc.Col(
            children=[
                dbc.Button(
                    "Add",
                    color="primary",
                    id="add-btn",
                    className="mt-4",
                    size="md"
                ),
            ],
            width=2,
        ),
    ],
    style=dict(display="none"),
    id="strategy_entry_row",
    className="mt-4",
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
                    size="md"
                ),
            ]
        ),
    ],
    id="strategy_list_row",
    style=dict(display="none"),
    className="mt-4",
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
        html.Div(id="dummy-div"),
    ],
)


@app.callback(
    Output("a_spot", "children"),
    Output("a_weeks", "options"),
    Output("strategy_entry_row", "style"),
    [Input("lookup-btn", "n_clicks")],
    [
        State("a_ticker", "value"),
    ],
)
def on_lookup_click(n, ticker):
    """Lookup the current price of ticker

    Args:
        n (_type_): Number of clicks of button to prevent being called during onLoad
        ticker (_type_): Symbol for which price needs to be fetched

    Returns:
        int: Ticker Price
        dict: Style to make strategy entry row visible
    """
    if n is None:
        raise PreventUpdate
    else:

        # quotes = Quotes()
        # res = quotes.get_quotes(ticker)
        # mark = res["mark"]
        mark, weeks = option_analysis.get_ticker_details(ticker=ticker)
        mark=formatter_number_2_digits(mark)
        return mark, weeks, dict()


@app.callback(
    Output("a_content", "children"),
    Output("strategy_list_row", "style"),
    [Input("add-btn", "n_clicks")],
    [
        State("a_contractType", "value"),
        State("a_tran_type", "value"),
        State("a_premium", "value"),
        State("a_lot", "value"),
        State("a_strike", "value"),
    ],
)
def on_add_click(n, op_type, tr_type, op_pr, contract, strike):
    """_summary_

    Args:
        n (_type_): _description_
        op_type (_type_): _description_
        tr_type (_type_): _description_
        op_pr (_type_): _description_
        contract (_type_): _description_
        strike (_type_): _description_
        cache_data (_type_): _description_

    Returns:
        _type_: _description_
    """
    if n is None:
        cache.clear()
        raise PreventUpdate
    else:
        contract_obj = {
            # "key": n,
            "op_type": op_type,
            "tr_type": tr_type,
            "op_pr": op_pr,
            "contract": contract,
            "strike": strike,
        }
        cache_obj = cache.get("strategy_list")
        if not cache_obj:
            cache_obj = []
        cache_obj.append(contract_obj)
        cache.set("strategy_list", cache_obj)
        # Display the strategies selected
        df = pd.DataFrame.from_dict(cache_obj)

        table_columns = [
            {"title": "OPTION", "field": "op_type", "editor": "input"},
            {"title": "BUY", "field": "tr_type", "editor": "input"},
            {"title": "PREMIUM", "field": "op_pr", "editor": "input"},
            {"title": "CONTRACT", "field": "contract", "editor": "input"},
            {"title": "STRIKE", "field": "strike", "editor": "input"},
        ]
        dt = (
            dash_tabulator.DashTabulator(
                id="analysis-table",
                columns=table_columns,
                data=df.to_dict("records"),
            ),
        )
        return dt, dict()


@app.callback(
    Output("graph_div", "children"),
    [Input("analysis-btn", "n_clicks"), Input("dummy-div", "children")],
    State("a_spot", "children"),
)
def on_analyze_click(n, dummy, spot_price):
    """_summary_

    Args:
        n (_type_): _description_
        cache_data (_type_): _description_
        spot_price (_type_): _description_

    Returns:
        _type_: _description_
    """
    if n is None:
        raise PreventUpdate
    else:
        cache_data = cache.get("strategy_list")
        spot = float(spot_price)
        fig = multi_plotter(spot=spot, op_list=cache_data)
        return dcc.Graph(figure=fig)


# dash_tabulator can register a callback on dataChanged
# to receive a dict of the row values
@app.callback(
    Output("dummy-div", "children"),
    Input("analysis-table", "dataChanged"),
)
def display_output(table):
    if table:
        # Update the cache object with datatable updates
        cache.set("strategy_list", table)
        return None
