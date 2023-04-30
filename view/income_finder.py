import dash_bootstrap_components as dbc
import dash_tabulator
from dash import dcc, html
from dash.dependencies import Input, Output, State

from app import app
from service.chart_helper import update_graph
from service.option_strategies import short_call, short_put, watchlist_income
from utils.constants import screener_list

TOP_COLUMN = dbc.Form(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            dbc.Label("Choose one"),
                            dbc.RadioItems(
                                options=[
                                    {"label": "SECURED PUT", "value": "PUT"},
                                    {"label": "COVERED CALL", "value": "CALL"},
                                ],
                                value="PUT",
                                id="contract_type",
                                inline=True,
                            ),
                        ]
                    ),
                ),
                dbc.Col(
                    html.Div(
                        [
                            dbc.Label("GroupTicker"),
                            dbc.Checklist(
                                options=[
                                    {"value": 1},
                                ],
                                value=[],
                                id="is_group",
                                switch=True,
                            ),
                        ]
                    ),
                ),
                dbc.Col(
                    html.Div(
                        [
                            dbc.Label("WatchList"),
                            dbc.Select(
                                options=[
                                    {"label": i, "value": i} for i in screener_list
                                ],
                                value="",
                                id="ticker_list",
                                placeholder="Select",
                            ),
                        ]
                    ),
                ),
                dbc.Col(
                    html.Div(
                        [
                            dbc.Label("Ticker"),
                            dbc.Input(
                                type="text",
                                id="ticker",
                                placeholder="Select for watchlist or Enter Ticker",
                            ),
                        ]
                    ),
                ),
            ],
            className="p-3",
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            dbc.Label("Min Days"),
                            dbc.Input(
                                type="text",
                                id="min_expiration_days",
                                placeholder="15",
                            ),
                        ]
                    ),
                ),
                dbc.Col(
                    html.Div(
                        [
                            dbc.Label("Max Days"),
                            dbc.Input(
                                type="text",
                                id="max_expiration_days",
                                placeholder="45",
                            ),
                        ]
                    ),
                ),
                dbc.Col(
                    html.Div(
                        [
                            dbc.Label("Min Delta"),
                            dbc.Input(
                                type="text",
                                id="min_delta",
                                placeholder="0.25",
                            ),
                        ]
                    ),
                ),
                dbc.Col(
                    html.Div(
                        [
                            dbc.Label("Max Delta"),
                            dbc.Input(
                                type="text",
                                id="max_delta",
                                placeholder="0.35",
                            ),
                        ]
                    ),
                ),
                dbc.Col(
                    html.Div(
                        [
                            dbc.Label("Premium %", html_for="premium"),
                            dbc.Input(
                                type="text",
                                id="premium",
                                placeholder="2",
                            ),
                        ]
                    ),
                ),
                dbc.Col(
                    html.Div(
                        [
                            dbc.Label("OTM %", html_for="moneyness"),
                            dbc.Input(
                                type="text",
                                id="moneyness",
                                placeholder="5",
                            ),
                        ]
                    ),
                ),
            ]
        ),
        html.Div(
            dbc.Button(
                "Search",
                color="primary",
                id="income-btn",
                outline=True,
            ),
            className="d-md-flex justify-content-md-end mt-3",
        ),
    ],
    className="p-3 bg-light border",
)
SEARCH_RESULT = html.Div(
    [
        html.Div(
            dbc.Alert(
                id="income-message",
                dismissable=True
            ),
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

layout = dbc.Container(
    [
        dbc.Row(TOP_COLUMN),
        html.P(),
        dbc.Row(SEARCH_RESULT),
    ],
    fluid=True,
)


@app.callback(
    [
        Output("income-output", "children"),
        Output("income-message", "is_open"),
        Output("income-message", "children"),
    ],
    [Input("income-btn", "n_clicks")],
    [
        State("contract_type", "value"),
        State("min_expiration_days", "value"),
        State("max_expiration_days", "value"),
        State("min_delta", "value"),
        State("max_delta", "value"),
        State("premium", "value"),
        State("moneyness", "value"),
        State("ticker", "value"),
        State("ticker_list", "value"),
        State("is_group", "value"),
    ],
)
def on_button_click(
    n,
    contract_type,
    min_expiration_days,
    max_expiration_days,
    min_delta,
    max_delta,
    premium,
    moneyness,
    ticker,
    ticker_list,
    is_group,
):
    if n is None:
        return None, False, ""
    else:
        params = {}
        func = None

        if contract_type == "PUT":
            func = short_put
        else:
            func = short_call

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

        if ticker:
            tickers = [ticker]
        elif ticker_list:
            tickers = screener_list.get(ticker_list)
        else:
            return None, True, "Enter Ticker or Select Watchlist"

        df = watchlist_income(tickers, params, func)
        if not df.empty:
            options = {
                "selectable": 1,
                "pagination": "local",
                "paginationSize": 20,
                "responsiveLayout": "true",
                "movableRows": "true",
            }

            # add groupBy option to the Tabulator component to group at Ticker level
            if is_group:
                options["groupBy"] = "TICKER"

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
