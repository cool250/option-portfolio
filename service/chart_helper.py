import logging
from datetime import datetime as dt
from datetime import timedelta
from statistics import mean

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from broker.history import History
from broker.search import Search
from utils.functions import formatter_number_2_digits

PERIOD = 30


def update_graph(ticker):

    endDate = dt.now()
    startDate = endDate - timedelta(days=120)

    # Retrieve Prices and volumes for a ticker
    history = History()
    df = history.get_price_historyDF(
        symbol=ticker,
        periodType="month",
        frequencyType="daily",
        frequency=1,
        startDate=startDate,
        endDate=endDate,
    )

    search = Search()
    company = search.search_instruments(symbol=ticker, projection="fundamental")

    # Get Company Fundamentals
    pe_ratio = company[ticker]["fundamental"]["peRatio"]
    peg_ratio = company[ticker]["fundamental"]["pegRatio"]
    eps = company[ticker]["fundamental"]["epsTTM"]

    description = company[ticker]["description"]


    low_period = min(df.low.tail(PERIOD))
    high_period = max(df.high.tail(PERIOD))
    mean_period = formatter_number_2_digits(mean(df.close.tail(PERIOD)))

    logging.info("low_30 %s high_30 %s", low_period, high_period)

    logging.info("end date is %s", df.iloc[-1].at["datetime"])
    logging.info("start date is %s", df.iloc[-21].at["datetime"])

    fig = make_subplots(
        rows=4,
        cols=1,
        row_heights=[0.5, 0.1, 0.2, 0.2],
        shared_xaxes=True,
        vertical_spacing=0.05,
    )

    # Stock price Candelstick -  Chart 1
    fig.add_trace(
        go.Candlestick(
            x=df["datetime"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name="Candle",
        ),
        row=1,
        col=1,
    )


    # shape defined programatically
    fig.add_shape(
        line_color="blue",
        type="line",
        xref="x1",
        yref="y1",
        x0=df.iloc[-21].at["datetime"],
        y0=low_period,
        x1=df.iloc[-1].at["datetime"],
        y1=low_period,
    )
    fig.add_shape(
        line_color="blue",
        type="line",
        xref="x1",
        yref="y1",
        x0=df.iloc[-21].at["datetime"],
        y0=high_period,
        x1=df.iloc[-1].at["datetime"],
        y1=high_period,
    )

    fig.add_annotation(
        y=high_period + 2,
        x=df.iloc[-21].at["datetime"],
        text="30 Day High : " + str(high_period),
        showarrow=False,
        xref="x1",
        yref="y1",
    )

    fig.add_annotation(
        y=low_period + 2,
        x=df.iloc[-21].at["datetime"],
        text="30 Day Low : " + str(low_period),
        showarrow=False,
        xref="x1",
        yref="y1",
    )


    # Update yaxis properties to show chart titles
    fig.update_yaxes(title_text="STOCK PRICE", showgrid=False, row=1, col=1)
    fig.update_yaxes(title_text="VOLUME", showgrid=False, row=2, col=1)

    fig.update(layout_xaxis_rangeslider_visible=False)
    fig.update_layout(
        height=800, title=ticker, template="plotly_white", showlegend=False,
    )

    info_text = f" {description} EPS:{eps} PE:{pe_ratio} PEG: {peg_ratio} 30D Avg close: {mean_period} "

    return fig, info_text
