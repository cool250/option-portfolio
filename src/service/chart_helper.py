import logging

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from service.trading_strategy import RsiBollingerBands

PERIOD = 30


# Function to show Bollinger chart
def show_charts(ticker: str):
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
    fig.add_trace(
        go.Scatter(x=df.index, y=df["rsi"], name="close", line_color="#CE2D2D"),
        row=2,
        col=1,
    )
    fig.add_hrect(
        y0=30,
        y1=70,
        line_width=2,
        fillcolor="red",
        opacity=0.2,
        row=2,
        col=1,
        annotation_text="RSI Band",
    )
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="RSI", row=2, col=1)
    fig.update_xaxes(title_text="Date", row=2, col=1)
    return fig
