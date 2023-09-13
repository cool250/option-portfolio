import logging
import multiprocessing
from datetime import datetime, timedelta

import pandas as pd
from joblib import Parallel, delayed

from broker.history import History
from broker.quotes import Quotes
from utils.constants import screener_list
from utils.functions import date_from_milliseconds

num_cores = multiprocessing.cpu_count()


class RsiBollingerBands:
    """
    RsiBollingerBands class implements a trading strategy using RSI and Bollinger Bands.

    Parameters:

        ticker (str): The stock symbol to trade

    Attributes:

        ticker (str): The stock symbol
        params:
            rsi_period (int): Period for calculating RSI
            bb_period (int): Period for calculating Bollinger Bands
            bb_dev (int): Standard deviation multiplier for Bollinger Bands
            oversold (int): RSI below this level is considered oversold
            overbought (int): RSI above this is considered overbought
    """

    DEFAULT_PARAMS = {
        "rsi_period": 14,
        "bb_period": 20,
        "bb_dev": 2,
        "oversold": 30,
        "overbought": 70,
        "chart_period": 90,
    }

    def __init__(self, ticker: str):
        self.ticker = ticker
        self.params = self.DEFAULT_PARAMS.copy()

    def analyze_ticker(self) -> tuple:
        """
        Generates historical data, calculates indicators, identifies signals,
         and returns DataFrames for charting.

         Returns:
             (df, buy, sell, price):
                 df (DataFrame): Contains close price, bands, RSI, SMA
                 buy (DataFrame): Buy signals
                 sell (DataFrame): Sell signals
                 price (float): Current price
        """
        now = datetime.now()
        start = now - timedelta(days=self.params["chart_period"])
        data = self.get_historical_prices(start, now)

        if data.empty:
            raise SystemError(
                f"Historical Prices not available for ticker: {self.ticker}"
            )

        df, current_price = self.prepare_dataframe(data)
        # Buy when close price is below lower band and sell when above upper band
        buy = df[df["close"] <= df["lower"]]
        sell = df[df["close"] >= df["upper"]]

        return df, buy, sell, current_price

    def prepare_dataframe(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        This method appends the current price to the historical close prices, calculates Bollinger Bands, RSI, and SMA,
        and drops initial rows (less than bb_period) where Bollinger Bands are not populated.

        Parameters:
            data (pd.DataFrame): The historical price data as a DataFrame.

        Returns:
            Tuple[pd.DataFrame, float]: A tuple containing the prepared DataFrame and the current price.
                - The prepared DataFrame contains the following columns:
                    - close (float): Historical close prices.
                    - upper (float): Upper Bollinger Band values.
                    - lower (float): Lower Bollinger Band values.
                    - rsi (float): Relative Strength Index values.
                    - sma (float): Simple Moving Average values.

                - The current price is a float representing the most recent price.
        """
        df = data[["close"]].copy()
        # Append current price to historical close prices to include today's price
        current_price, date = self.get_current_price()
        index = date
        df.loc[index] = current_price
        sma, upper_band, lower_band = self.get_bollinger_bands(df)
        rsi = self.get_rsi(df)
        df = df.join(upper_band).join(lower_band)
        df = df.join(rsi).join(sma)
        # Drop rows for initial dates where bollinger bands are not poplulated
        df = df.dropna(subset=["lower"])
        return df, current_price

    def get_bollinger_bands(self, df: pd.DataFrame, sma: bool = True) -> tuple:
        """
        Calculates SMA, Upper Band, Lower Band for given DataFrame.

        Parameters:
            df (DataFrame): Dataframe with close prices

        Returns:
            sma, upper_band, lower_band (Series):
                Containing SMA, Upper Band, Lower Band
        """
        period = self.params["bb_period"]
        std_dev = self.params["bb_dev"]

        if sma:
            sma = df.rolling(window=period).mean().dropna()
            std = df.rolling(window=period).std().dropna()
            upper_band = sma + std_dev * std
            lower_band = sma - std_dev * std
        else:
            raise NotImplementedError("Only SMA available")

        upper_band = upper_band.rename(columns={"close": "upper"})
        lower_band = lower_band.rename(columns={"close": "lower"})
        sma = sma.rename(columns={"close": "sma"})

        return sma, upper_band, lower_band

    def get_rsi(self, df: pd.DataFrame, ema: bool = True):
        """
        Calculates Relative Strength Index for given DataFrame.

        Parameters:
            df (DataFrame): Dataframe with close prices

        Returns:
            rsi (DataFrame): DataFrame containing RSI values
        """
        periods = self.params["rsi_period"]
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
        rsi = rsi.rename(columns={"close": "rsi"})
        return rsi

    def get_historical_prices(self, start: datetime, end: datetime) -> pd.DataFrame:
        """
        Fetches historical price data from API.

        Parameters:
            start (datetime): Start date
            end (datetime): End date

        Returns:
            df (DataFrame): Historical prices
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
            logging.error(f"Error fetching historical prices for {stock}: {str(e)}")
            return pd.DataFrame()

    def get_current_price(self) -> tuple[str, str]:
        """
        Fetches current price from API.

        Returns:
            price (float): Current price
            date (datetime): Date of current price
        """

        stock = self.ticker
        try:
            c = Quotes()
            r = c.get_quotes(stock)
            price = r[stock]["lastPrice"]
            date = date_from_milliseconds(r[stock]["quoteTimeInLong"])
            return price, date
        except Exception as e:
            logging.error(f"Error fetching current price for {stock}: {str(e)}")
            return None, None


def get_trade_signal(ticker: str, trade_type: str):
    """
    Generates a trading signal for a given ticker and trade type (buy or sell) using the RsiBollingerBands strategy.

    Parameters:
        ticker (str): The stock symbol to generate a signal for.
        trade_type (str): The type of trade signal to generate, either 'buy' or 'sell'.

    Returns:
        tuple or None: A tuple containing the following information if a signal is generated:
            - Ticker (str): The stock symbol.
            - Date (datetime): The date of the trade signal.
            - Price (float): The price at which the trade signal was generated.
            - Current_Price (float): The current price of the stock.
        Returns None if no signal is generated or an error occurs.
    """
    strategy = RsiBollingerBands(ticker)
    try:
        _, buy, sell, current_price = strategy.analyze_ticker()
        trade_type = buy if trade_type == "buy" else sell
        latest_trade = trade_type.tail(1)

        if latest_trade.empty:
            return None

        date = latest_trade.index[0]
        price = latest_trade["close"][0]

    except Exception as e:
        logging.error(f" Error in trade signal for ticker {ticker} : {str(e)}")
        return None
    return (
        ticker,
        date,
        price,
        current_price,
    )


def analyze_watchlist(ticker_list: str, trade_type: str) -> pd.DataFrame:
    """
    Analyzes a list of tickers from a watchlist and generates trade signals for each ticker.

    Parameters:
        ticker_list (str): The name of the watchlist containing the tickers to analyze.
        trade_type (str): The type of trade signal to generate, either 'buy' or 'sell'.

    Returns:
        A DataFrame containing trade signal information for the tickers in the watchlist, or None if an error occurs during the analysis.

        - If trade signals are generated for one or more tickers, the DataFrame will have the following columns:
            - Ticker (str): The stock symbol.
            - Date (datetime): The date of the trade signal.
            - Price (float): The price at which the trade signal was generated.
            - Current_Price (float): The current price of the stock.

        - If no trade signals are generated for any ticker in the watchlist, an empty DataFrame is returned.

        - If an error occurs during the analysis, None is returned, and an error message is logged.
    """
    tickers = screener_list.get(ticker_list)
    df = pd.DataFrame()
    try:
        results = Parallel(n_jobs=num_cores)(
            delayed(get_trade_signal)(i, trade_type) for i in tickers
        )
        #  Aggregate the results
        for result in results:
            if result:
                ticker_row = {
                    "Ticker": result[0],
                    "Date": result[1],
                    "Price": result[2],
                    "Current_Price": result[3],
                }
                df2 = pd.DataFrame([ticker_row])
                df = pd.concat([df, df2], ignore_index=True)
        return df
    except Exception as e:
        logging.error(f"Error running Parallel: {str(e)}")
        return None
