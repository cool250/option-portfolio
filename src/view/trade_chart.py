import dash_bootstrap_components as dbc
import dash_tabulator
import plotly.graph_objects as go
from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate
from plotly.subplots import make_subplots

from app import app
from service.trading_strategy import RsiBollingerBands, buy_stocks

# Define constants
TOP_COLUMN = dbc.Form(
    [
        dbc.Row(
            [
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
                            "Search",
                            color="primary",
                            id="bollinger-btn",
                            className="mt-4",
                            size="md",
                        ),
                    ],
                    className="text-end",
                ),
                dbc.Col(
                    width=1,
                    children=[
                        dbc.Button(
                            "Scan",
                            color="secondary",
                            id="scan-btn",
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
        dbc.Row(SCREENED_STOCKS),
        html.P(),
        dbc.Row(CHART_LAYOUT),
    ],
)


@app.callback(
    Output("stock_screener", "children"),
    Input("scan-btn", "n_clicks"),
)
def scan_stocks(n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    else:
        df = buy_stocks()
        dt = (
            dash_tabulator.DashTabulator(
                id="screener-table",
                columns=[{"id": i, "title": i, "field": i} for i in df.columns],
                data=df.to_dict("records"),
            ),
        )
        return dt


# Callback for button click
@app.callback(
    Output("bollinger_content", "children"),
    [Input("bollinger-btn", "n_clicks")],
    [State("bollinger-ticker", "value")],
)
def on_search(n_clicks: int, ticker: str) -> dbc.Container:
    """
    Callback triggered when the search button is clicked.

    Args:
        n_clicks (int): The number of times the button has been clicked.
        ticker (str): The ticker symbol entered by the user.

    Returns:
        dash.Container: A container with the Bollinger chart or an alert if no records are found.
    """
    if n_clicks is None or not ticker.strip():
        raise PreventUpdate
    return dbc.Container([dbc.Row([dbc.Col(show_charts(ticker.strip().upper()))])])


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
    df, buy, sell, _ = strategy.analyze_strategy()

    # Initialize figure with subplots
    fig = make_subplots(rows=2, cols=1, row_heights=[0.7, 0.3])
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
    fig.add_trace(
        go.Scatter(x=df.index, y=df["rsi"], name="close", line_color="#CE2D2D"),
        row=2,
        col=1,
    )
    content = dcc.Graph(figure=fig)
    return content
