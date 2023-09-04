from datetime import datetime, timedelta

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

from app import app
from broker.history import History
from broker.quotes import Quotes
from utils.functions import date_from_milliseconds

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
)


# Callback for button click
@app.callback(
    Output("bollinger_content", "children"),
    [Input("bollinger-btn", "n_clicks")],
    [State("bollinger-ticker", "value")],
)
def on_page_load(n_clicks, ticker):
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
    return dbc.Container(
        [dbc.Row([dbc.Col(show_bollinger_chart(ticker.strip().upper()))])]
    )


# Function to show Bollinger chart
def show_bollinger_chart(ticker):
    """
    Generate and display a Bollinger Bands chart for the specified stock ticker.

    Args:
        ticker (str): The stock ticker symbol.

    Returns:
        dash.Graph: A Plotly graph containing the Bollinger Bands chart.
    """
    now = datetime.now()
    start = now - timedelta(days=365)
    data = get_prices(ticker, start, now)

    if data.empty:
        return html.Div(
            dbc.Alert(id="total-message", children="No records found", color="info"),
        )

    df = data[["close"]]

    # Append current price to historical close prices
    price, date_time = get_current_price(ticker)
    curent_price_row = {"close": price}
    df.loc[date_time] = curent_price_row

    sma = df.rolling(window=20).mean().dropna()
    std = df.rolling(window=20).std().dropna()
    upper_band = sma + 2 * std
    lower_band = sma - 2 * std

    upper_band = upper_band.rename(columns={"close": "upper"})
    lower_band = lower_band.rename(columns={"close": "lower"})
    bb = df.join(upper_band).join(lower_band)
    bb = bb.dropna()

    # Buy when close price is below lower band and sell when above upper band
    buy = bb[bb["close"] <= bb["lower"]]
    sell = bb[bb["close"] >= bb["upper"]]

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
            x=buy.index,
            y=buy["close"],
            name="Buy",
            mode="markers",
            marker=dict(
                color="#00CC96",
                size=10,
            ),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=sell.index,
            y=sell["close"],
            name="Sell",
            mode="markers",
            marker=dict(
                color="#EF553B",
                size=10,
            ),
        )
    )
    content = dcc.Graph(figure=fig)
    return content


def get_prices(stock, start, end):
    """
    Fetch historical price data for the specified stock symbol within a given date range.

    Args:
        stock (str): The stock ticker symbol.
        start (datetime): The start date for fetching historical data.
        end (datetime): The end date for fetching historical data.

    Returns:
        pandas.DataFrame: A DataFrame containing historical price data.
    """
    try:
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
    except Exception as e:
        print(f"Error fetching prices for {stock}: {str(e)}")
        return pd.DataFrame()


def get_current_price(stock):
    """
    Fetch the current price and timestamp for the specified stock symbol.
    This is appended to historical price

    Args:
        stock (str): The stock ticker symbol.

    Returns:
        float: The current stock price.
        datetime: The timestamp of the stock price.
    """
    try:
        c = Quotes()
        r = c.get_quotes(stock)
        price = r[stock]["lastPrice"]
        date_time = date_from_milliseconds(r[stock]["quoteTimeInLong"])
        return price, date_time
    except Exception as e:
        print(f"Error fetching current price for {stock}: {str(e)}")
        return None, None
