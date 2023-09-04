from datetime import datetime, timedelta

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

from app import app
from broker.history import History
from broker.quotes import Quotes
from utils.functions import date_from_milliseconds

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
                            placeholder="symbol",
                            size="sm",
                        ),
                    ],
                ),
                dbc.Col(
                    width=2,
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
            ],
        ),
    ],
    className="p-2",
)
CHART_LAYOUT = html.Div(id="bollinger_content")

layout = dbc.Container(
    [
        dbc.Row(TOP_COLUMN),
        html.P(),
        dbc.Row(CHART_LAYOUT),
    ],
    fluid=True,
)


@app.callback(
    Output("bollinger_content", "children"),
    [
        Input("bollinger-btn", "n_clicks"),
    ],
    [
        State("bollinger-ticker", "value"),
    ],
)
def on_page_load(n, ticker):
    if n is None:
        raise PreventUpdate
    else:
        return dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(show_bollinger_chart(ticker)),
                    ]
                ),
            ]
        )


def show_bollinger_chart(ticker):
    now = datetime.now()
    start = now - timedelta(days=365)
    data = get_prices(ticker, start, now)
    if not data.empty:
        df = data[["close"]]
        sma = df.rolling(window=20).mean().dropna()
        rstd = df.rolling(window=20).std().dropna()
        upper_band = sma + 2 * rstd
        lower_band = sma - 2 * rstd

        upper_band = upper_band.rename(columns={"close": "upper"})
        lower_band = lower_band.rename(columns={"close": "lower"})
        bb = df.join(upper_band).join(lower_band)
        bb = bb.dropna()

        upper = upper_band["upper"].iloc[-1]
        lower = lower_band["lower"].iloc[-1]

        buyers = bb[bb["close"] <= bb["lower"]]
        sellers = bb[bb["close"] >= bb["upper"]]

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=lower_band.index,
                y=lower_band["lower"],
                name="Lower Band",
                line_color="rgba(173,204,255,0.2)",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=upper_band.index,
                y=upper_band["upper"],
                name="Upper Band",
                fill="tonexty",
                fillcolor="rgba(173,204,255,0.2)",
                line_color="rgba(173,204,255,0.2)",
            )
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=df["close"], name="close", line_color="#636EFA")
        )
        fig.add_trace(
            go.Scatter(x=sma.index, y=sma["close"], name="SMA", line_color="#FECB52")
        )
        fig.add_trace(
            go.Scatter(
                x=buyers.index,
                y=buyers["close"],
                name="Buyers",
                mode="markers",
                marker=dict(
                    color="#00CC96",
                    size=10,
                ),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=sellers.index,
                y=sellers["close"],
                name="Sellers",
                mode="markers",
                marker=dict(
                    color="#EF553B",
                    size=10,
                ),
            )
        )
        content = dcc.Graph(figure=fig)
        return content
    else:
        return html.Div(
            dbc.Alert(id="total-message", children="No records found", color="info"),
        )


def get_prices(stock, start, end):
    # fetch price history using tda-api
    c = History()

    df = c.get_price_historyDF(
        symbol=stock,
        startDate=start,
        endDate=end,
        periodType="month",
        frequencyType="daily",
        frequency=1,
        needExtendedHoursData=False,
    )

    return df


# function to retrive current price of stock
def get_cur_price(stock):
    c = Quotes()
    r = c.get_quotes(stock)
    price = r[stock]["lastPrice"]
    date_time = date_from_milliseconds(r[stock]["quoteTimeInLong"])

    return price, date_time
