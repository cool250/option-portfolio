import logging

import dash_bootstrap_components as dbc
import dash_tabulator
import plotly.graph_objects as go
from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate
from plotly.subplots import make_subplots

from app import app
from service.trading_strategy import RsiBollingerBands, analyze_watchlist
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


@app.callback(
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
@app.callback(
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
    return (
        dbc.Container([dbc.Row([dbc.Col(show_charts(ticker.strip().upper()))])]),
        None,
    )


# Function to show Bollinger chart
def show_charts(ticker: str) -> dcc.Graph:
    """
    Generate and display a Bollinger Bands chart for the specified stock ticker.

    Args:
        ticker (str): The stock ticker symbol.

    Returns:
        dash.Graph: A Plotly graph containing the Bollinger Bands chart.
    """

    strategy = RsiBollingerBands(ticker)
    try:
        df, buy, sell, _ = strategy.analyze_ticker()
    except Exception as e:
        logging.error(f"Error calling analyze_ticker for ticker {ticker} {str(e)}")
        return "No Results Found"

    # Initialize figure with subplots
    fig = make_subplots(
        rows=2,
        cols=1,
        row_heights=[0.7, 0.3],
        shared_xaxes=True,
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["lower"],
            name="Lower Band",
            line_color="rgba(173,204,255,0.2)",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["upper"],
            name="Upper Band",
            fill="tonexty",
            fillcolor="rgba(173,204,255,0.2)",
            line_color="rgba(173,204,255,0.2)",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df["close"], name="close", line_color="#636EFA"),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df["sma"], name="SMA", line_color="#FECB52"),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=buy.index,
            y=buy["close"],
            name="Buy",
            mode="markers",
            marker=dict(
                color="#00CC96",
                size=8,
            ),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=sell.index,
            y=sell["close"],
            name="Sell",
            mode="markers",
            marker=dict(
                color="#EF553B",
                size=8,
            ),
        ),
        row=1,
        col=1,
    )
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.add_trace(
        go.Scatter(x=df.index, y=df["rsi"], name="close", line_color="#CE2D2D"),
        row=2,
        col=1,
    )
    fig.add_hline(
        y=30, line_dash="dash", line_width=3, line_color="black", row=2, col=1
    )
    fig.add_hline(
        y=70, line_dash="dash", line_width=3, line_color="black", row=2, col=1
    )
    fig.update_layout(
        height=600,
        width=1200,
    )
    fig.update_yaxes(title_text="RSI", row=2, col=1)
    fig.update_xaxes(title_text="Date")
    content = dcc.Graph(figure=fig)
    return content
