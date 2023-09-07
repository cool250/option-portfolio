from datetime import datetime, timedelta

import pandas as pd

from broker.history import History
from broker.quotes import Quotes
from utils.functions import date_from_milliseconds


class RsiBollingerBands:
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.rsi_period = 14
        self.bb_period = 20
        self.bb_dev = 2
        self.oversold = 30
        self.overbought = 70

    # Function to show Bollinger chart
    def generate_chart_data(self) -> tuple:
        """
        Generate and display a Bollinger Bands chart for the specified stock ticker.

        Args:
            ticker (str): The stock ticker symbol.

        Returns:
            dash.Graph: A Plotly graph containing the Bollinger Bands chart.
        """
        now = datetime.now()
        start = now - timedelta(days=365)
        data = self.get_historical_prices(start, now)

        if data.empty:
            raise NotImplementedError()

        df = data[["close"]].copy()

        # Append current price to historical close prices
        price, date = self.get_current_price()
        index = date
        df.loc[index] = price

        sma, upper_band, lower_band = self.get_bollinger_bands(df)
        rsi = self.get_rsi(df)

        bb = df.join(upper_band).join(lower_band)
        bb = bb.dropna()

        # Buy when close price is below lower band and sell when above upper band
        buy = bb[bb["close"] <= bb["lower"]]
        sell = bb[bb["close"] >= bb["upper"]]

        return df, buy, sell, rsi, sma, upper_band, lower_band, price

    def get_bollinger_bands(self, df: pd.DataFrame, sma: bool = True) -> tuple:
        """
        Calculate Bollinger Bands for a given DataFrame of financial data.

        Parameters:
            df (pd.DataFrame): The DataFrame containing financial data, including a 'close' column.
            sma (bool, optional): Whether to use Simple Moving Average (SMA) for Bollinger Bands. Default is True.

        Returns:
            tuple: A tuple containing the following elements:
                - sma (pd.Series): The Simple Moving Average (SMA) of the 'close' prices.
                - upper_band (pd.Series): The upper Bollinger Band values.
                - lower_band (pd.Series): The lower Bollinger Band values.
                - buy (pd.DataFrame): DataFrame of buy signals (close price below lower band).
                - sell (pd.DataFrame): DataFrame of sell signals (close price above upper band).

        Raises:
            NotImplementedError: If sma is set to False, as only SMA calculation is currently supported.

        Usage:
            sma, upper_band, lower_band, buy, sell = get_bollinger_bands(df, periods=20, sma=True)
        """
        period = self.bb_period
        std_dev = self.bb_dev

        if sma:
            sma = df.rolling(window=period).mean().dropna()
            std = df.rolling(window=period).std().dropna()
            upper_band = sma + std_dev * std
            lower_band = sma - std_dev * std
        else:
            raise NotImplementedError("Only SMA available")

        upper_band = upper_band.rename(columns={"close": "upper"})
        lower_band = lower_band.rename(columns={"close": "lower"})

        return sma, upper_band, lower_band

    def get_rsi(self, df: pd.DataFrame, ema: bool = True):
        """
        Returns a pd.Dataframe with the relative strength index.
        """
        periods = self.rsi_period
        close_delta = df["close"].diff()

        # Make two series: one for lower closes and one for higher closes
        up = close_delta.clip(lower=0)
        down = -1 * close_delta.clip(upper=0)

        if ema:
            # Use exponential moving average
            ma_up = up.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
            ma_down = down.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
        else:
            # Use simple moving average
            ma_up = up.rolling(window=periods, adjust=False).mean()
            ma_down = down.rolling(window=periods, adjust=False).mean()

        rsi = ma_up / ma_down
        rsi = 100 - (100 / (1 + rsi))
        rsi = rsi.to_frame()
        return rsi

    def get_historical_prices(self, start: datetime, end: datetime) -> pd.DataFrame:
        """
        Fetch historical price data for the specified stock symbol within a given date range.

        Args:
            stock (str): The stock ticker symbol.
            start (datetime): The start date for fetching historical data.
            end (datetime): The end date for fetching historical data.

        Returns:
            pandas.DataFrame: A DataFrame containing historical price data.
        """
        stock = self.ticker
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

    def get_current_price(self) -> tuple[str, str]:
        """
        Fetch the current price and timestamp for the specified stock symbol.
        This is appended to historical price

        Args:
            stock (str): The stock ticker symbol.

        Returns:
            float: The current stock price.
            date: The date of the stock price.
        """

        stock = self.ticker
        try:
            c = Quotes()
            r = c.get_quotes(stock)
            price = r[stock]["lastPrice"]
            date = date_from_milliseconds(r[stock]["quoteTimeInLong"])
            return price, date
        except Exception as e:
            print(f"Error fetching current price for {stock}: {str(e)}")
            return None, None
