import dash_bootstrap_components as dbc
import dash_tabulator
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app
from service.chart_helper import update_graph
from service.search_income import watchlist_income
from utils.constants import screener_list

SIDE_COLUMN = (
    html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        children=[
                            dbc.Label("Instrument Type", size="sm"),
                            dbc.Select(
                                options=[
                                    {"label": "PUT", "value": "PUT"},
                                    {"label": "CALL", "value": "CALL"},
                                ],
                                value="PUT",
                                id="contractType",
                                size="sm",
                            ),
                        ],
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        children=[
                            dbc.Label("Ticker", size="sm"),
                            dbc.Input(
                                type="text",
                                id="ticker",
                                size="sm",
                            ),
                        ],
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        children=[
                            dbc.Label("WatchList", size="sm"),
                            dbc.Select(
                                options=[
                                    {"label": i, "value": i} for i in screener_list
                                ],
                                value="",
                                id="ticker_list",
                                placeholder="Select",
                                size="sm",
                            ),
                        ],
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        children=[
                            dbc.Label("Premium %", size="sm"),
                            dbc.Input(
                                type="text",
                                id="premium",
                                placeholder="1",
                                size="sm",
                            ),
                        ],
                    ),
                    dbc.Col(
                        children=[
                            dbc.Label("OTM %", size="sm"),
                            dbc.Input(
                                type="text",
                                id="moneyness",
                                placeholder="2",
                                size="sm",
                            ),
                        ],
                    ),
                ],
            ),
            dbc.Row(
                [
                    dbc.Col(
                        children=[
                            dbc.Label("Min Days", size="sm"),
                            dbc.Input(
                                type="text",
                                id="min_expiration_days",
                                placeholder="15",
                                size="sm",
                            ),
                        ],
                    ),
                    dbc.Col(
                        children=[
                            dbc.Label("Max Days", size="sm"),
                            dbc.Input(
                                type="text",
                                id="max_expiration_days",
                                placeholder="45",
                                size="sm",
                            ),
                        ],
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        children=[
                            dbc.Label("Min Delta", size="sm"),
                            dbc.Input(
                                type="text",
                                id="min_delta",
                                placeholder="0.25",
                                size="sm",
                            ),
                        ],
                    ),
                    dbc.Col(
                        children=[
                            dbc.Label("Max Delta", size="sm"),
                            dbc.Input(
                                type="text",
                                id="max_delta",
                                placeholder="0.35",
                                size="sm",
                            ),
                        ],
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        children=[
                            dbc.Button(
                                "Search",
                                color="primary",
                                id="income-btn",
                                className="mt-4",
                            ),
                        ],
                    ),
                ],
                class_name="text-end",
            ),
        ],
    ),
)
SEARCH_RESULT = html.Div(
    [
        html.Div(
            dbc.Alert(id="income-message", dismissable=True, is_open=False),
        ),
        dbc.Modal(
            [
                dbc.ModalHeader("Charts"),
                dbc.ModalBody(
                    id="chart-output",
                ),
            ],
            id="modal-chart",
            size="xl",
        ),
        html.Div(dbc.Spinner(html.Div(id="income-output"))),
    ]
)

layout = dbc.Form(
    [
        dbc.Row(
            [
                dbc.Col(SIDE_COLUMN, width=2, className="p-2 bg-light border"),
                dbc.Col(SEARCH_RESULT, width=10),
            ],
        )
    ],
)


@app.callback(
    [
        Output("income-output", "children"),
        Output("income-message", "is_open"),
        Output("income-message", "children"),
    ],
    [Input("income-btn", "n_clicks")],
    [
        State("contractType", "value"),
        State("min_expiration_days", "value"),
        State("max_expiration_days", "value"),
        State("min_delta", "value"),
        State("max_delta", "value"),
        State("premium", "value"),
        State("moneyness", "value"),
        State("ticker", "value"),
        State("ticker_list", "value"),
    ],
)
def on_button_click(
    n,
    contractType,
    min_expiration_days,
    max_expiration_days,
    min_delta,
    max_delta,
    premium,
    moneyness,
    ticker,
    ticker_list,
):
    """
    Callback function triggered on button click to perform income search.

    Args:
        n (int): Number of button clicks.
        contractType (str): Selected instrument type.
        min_expiration_days (int): Minimum expiration days.
        max_expiration_days (int): Maximum expiration days.
        min_delta (float): Minimum delta.
        max_delta (float): Maximum delta.
        premium (str): Premium value.
        moneyness (str): Moneyness value.
        ticker (str): Ticker input.
        ticker_list (str): Selected watchlist.

    Returns:
        tuple: A tuple of results to update the income output, message visibility, and message content.
    """
    if n is None:
        raise PreventUpdate
    else:
        params = {}

        params["contractType"] = contractType
        if min_expiration_days:
            params["min_expiration_days"] = int(min_expiration_days)
        if max_expiration_days:
            params["max_expiration_days"] = int(max_expiration_days)
        if min_delta:
            params["min_delta"] = float(min_delta)
        if max_delta:
            params["max_delta"] = float(max_delta)
        if premium:
            params["premium"] = premium
        if moneyness:
            params["moneyness"] = moneyness

        # Convert ticker to list for consistency with ticker list
        # Ticker can take comma seperated values
        if ticker:
            tickers = ticker.split(",")
            tickers = [item.strip() for item in tickers]  # strip any whitespace
        elif ticker_list:
            tickers = screener_list.get(ticker_list)
        else:
            return None, True, "Enter Ticker or Select Watchlist"

        df = watchlist_income(tickers, params)
        if not df.empty:
            options = {
                "selectable": 1,
                "pagination": "local",
                "paginationSize": 20,
                "responsiveLayout": "true",
                "movableRows": "true",
                "groupBy": "TICKER",
            }

            dt = (
                dash_tabulator.DashTabulator(
                    id="screener-table",
                    columns=[{"id": i, "title": i, "field": i} for i in df.columns],
                    data=df.to_dict("records"),
                    options=options,
                ),
            )
            return dt, False, ""

        else:
            return None, True, "No Results Found"


# dash_tabulator can register a callback on rowClicked
# to receive a dict of the row values
@app.callback(
    [
        Output("chart-output", "children"),
        Output("modal-chart", "is_open"),
    ],
    [Input("screener-table", "rowClicked")],
)
def display_output(value):
    """
    Callback function triggered when a row is clicked in the table to display the corresponding chart.

    Args:
        value (dict): The row values of the clicked row.

    Returns:
        tuple: A tuple of results to update the chart output and modal visibility.
    """
    if value:
        # Get the ticker symbol from dataframe by passing selected row and column which has the tickers
        ticker = value["TICKER"]
        fig, info_text = update_graph(ticker)
        chart = html.Div(
            [
                dbc.Alert(info_text, color="primary"),
                dcc.Graph(figure=fig),
            ]
        )
        return chart, True
    else:
        return "", False
