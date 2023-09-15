import dash_bootstrap_components as dbc
import dash_tabulator
from dash import Input, Output, State, callback, dcc, html
from dash.exceptions import PreventUpdate

from service.chart_helper import show_charts
from service.trading_strategy import analyze_watchlist
from utils.constants import screener_list

# Define constants
TOP_COLUMN = dbc.Form(
    [
        dbc.Row(
            [
                dbc.Col(
                    width=2,
                    children=[
                        dbc.Label("WatchList", size="sm"),
                        dbc.Select(
                            options=[{"label": i, "value": i} for i in screener_list],
                            value="",
                            id="ticker_list",
                            placeholder="Select",
                            size="sm",
                        ),
                    ],
                ),
                dbc.Col(
                    width=2,
                    children=[
                        dbc.Label("Trade Type", size="sm"),
                        dbc.Select(
                            id="trade_type",
                            options=[
                                {"label": "SELL", "value": "sell"},
                                {"label": "BUY", "value": "buy"},
                            ],
                            value="buy",
                            size="sm",
                        ),
                    ],
                ),
                dbc.Col(
                    width=2,
                    children=[
                        dbc.Button(
                            "Run Scan",
                            color="primary",
                            id="scan-btn",
                            className="mt-4",
                            size="md",
                        ),
                    ],
                ),
                dbc.Col(
                    width=2,
                    children=[
                        dbc.Label("Ticker", size="sm"),
                        dbc.Input(
                            type="text",
                            id="bollinger-ticker",
                            placeholder="Symbol",
                            size="sm",
                        ),
                    ],
                ),
                dbc.Col(
                    width=1,
                    children=[
                        dbc.Button(
                            "Go",
                            color="primary",
                            id="bollinger-btn",
                            className="mt-4",
                            size="md",
                        ),
                    ],
                    className="text-end",
                ),
            ],
        ),
    ],
    className="p-2",
)

SCREENED_STOCKS = html.Div(id="stock_screener")
CHART_LAYOUT = html.Div(id="bollinger_content")

layout = dbc.Container(
    [
        dbc.Row(TOP_COLUMN),
        html.P(),
        dbc.Spinner(
            children=[
                dbc.Row(SCREENED_STOCKS),
                dbc.Row(CHART_LAYOUT),
            ]
        ),
    ],
)


@callback(
    [Output("stock_screener", "children"), Output("bollinger_content", "children")],
    [Input("scan-btn", "n_clicks")],
    [State("ticker_list", "value"), State("trade_type", "value")],
)
def scan_stocks(n_clicks, ticker_list, trade_type):
    if n_clicks is None:
        raise PreventUpdate
    else:
        if len(ticker_list) == 0 or trade_type is None:
            raise PreventUpdate
        df = analyze_watchlist(ticker_list, trade_type)
        if not df.empty:
            dt = (
                dash_tabulator.DashTabulator(
                    id="screener-table",
                    columns=[{"id": i, "title": i, "field": i} for i in df.columns],
                    data=df.to_dict("records"),
                ),
            )
            return dt, None


# Callback for button click
@callback(
    [
        Output("bollinger_content", "children", allow_duplicate=True),
        Output("stock_screener", "children", allow_duplicate=True),
    ],
    [Input("bollinger-btn", "n_clicks")],
    [State("bollinger-ticker", "value")],
    prevent_initial_call=True,
)
def on_search(n_clicks: int, ticker: str) -> dbc.Container:
    """
    Callback triggered when the search button is clicked. It shows the chart and hides
    the stock screening table

    Args:
        n_clicks (int): The number of times the button has been clicked.
        ticker (str): The ticker symbol entered by the user.

    Returns:
        dash.Container: A container with the Bollinger chart or an alert if no records are found.
    """
    if n_clicks is None or not ticker.strip():
        raise PreventUpdate

    ticker = ticker.strip().upper()
    fig = show_charts(ticker)
    chart = dcc.Graph(figure=fig)
    return chart, None
