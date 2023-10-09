import logging
from datetime import datetime as dt
from datetime import timedelta

import numpy as np
import pandas as pd

from broker.account import Account
from broker.quotes import Quotes
from broker.user_config import UserConfig
from utils.enums import PUT_CALL
from utils.functions import convert_to_df, formatter_percent


class AccountPositions:
    def __init__(self):
        super().__init__()
        self.positions, self.balance = get_account()
        self.params_options = {
            "quantity": "QTY",
            "underlying": "TICKER",
            "symbol": "SYMBOL",
            "underlyingPrice": "UNDERLYING PRICE",
            "strikePrice": "STRIKE PRICE",
            "mark": "MARK",
            "intrinsic": "INTRINSIC",
            "extrinsic": "EXTRINSIC",
            "ITM": "ITM",
            "theta": "THETA",
            "delta": "DELTA",
            "averagePrice": "PURCHASE PRICE",
            "daysToExpiration": "DAYS",
            "maintenanceRequirement": "MARGIN",
        }

        self.params_stocks = {
            "quantity": "QTY",
            "underlying": "TICKER",
            "mark": "MARK",
            "averagePrice": "AVG COST",
            # "NET": "PROFIT/LOSS",
            "maintenanceRequirement": "MARGIN",
        }

    def get_put_positions(self):
        """
        Get all open Puts first from Accounts API and later pricing information
        for the symbol via Quotes
        """

        def addmoneyness(row):
            intrinsic = round(max(row["strikePrice"] - row["underlyingPrice"], 0), 2)
            extrinsic = round(row["mark"] - intrinsic, 2)
            itm = np.where(row["strikePrice"] > row["underlyingPrice"], "Y", "N")
            return intrinsic, extrinsic, itm

        positions = self.positions
        # Filter for puts
        is_put = positions["option_type"] == PUT_CALL.PUT.value
        df = positions[is_put]

        res_df = pd.DataFrame()
        res_df[["intrinsic", "extrinsic", "ITM"]] = df.apply(
            addmoneyness, axis=1, result_type="expand"
        )
        df = df.join(res_df)

        if not df.empty:
            #  Retain only the columns needed and rename
            df = df[self.params_options.keys()]
            df["theta"] = df["theta"] * df["quantity"] * 100
            df["delta"] = df["delta"] * df["quantity"] * 100
            df.rename(columns=self.params_options, inplace=True)
        # Add liquidity for Puts if assigned
        df["COST"] = df["STRIKE PRICE"] * df["QTY"].abs() * 100
        df["RETURNS"] = (
            (((df["MARK"] * 365 * df["QTY"] * 100) / (df["MARGIN"] * df["DAYS"])))
            .abs()
            .apply(formatter_percent)
        )
        df["PREMIUM"] = df["PURCHASE PRICE"] * df["QTY"].abs() * 100
        df["CLOSE_DATE"] = df["DAYS"].apply(lambda x: dt.now() + timedelta(x))
        df = df.round(2)
        df = df.sort_values(by=["DAYS"])
        return df

    def get_call_positions(self):
        """
        Get all open Calls first from Accounts API and later pricing information
        for the symbol via Qouotes
        """

        def addmoneyness(row):
            intrinsic = round(max(row["underlyingPrice"] - row["strikePrice"], 0), 2)
            extrinsic = round(row["mark"] - intrinsic, 2)
            itm = np.where(row["strikePrice"] < row["underlyingPrice"], "Y", "N")
            return intrinsic, extrinsic, itm

        positions = self.positions

        # Filter for calls
        is_call = positions["option_type"] == PUT_CALL.CALL.value
        df = positions[is_call]

        res_df = pd.DataFrame()
        res_df[["intrinsic", "extrinsic", "ITM"]] = df.apply(
            addmoneyness, axis=1, result_type="expand"
        )
        df = df.join(res_df)

        if not df.empty:
            #  Retain only the columns needed and rename
            df = df[self.params_options.keys()]
            df["theta"] = df["theta"] * df["quantity"] * 100
            df["delta"] = df["delta"] * df["quantity"] * 100
            df.rename(columns=self.params_options, inplace=True)

        df["PREMIUM"] = df["PURCHASE PRICE"] * df["QTY"].abs() * 100
        df["CLOSE_DATE"] = df["DAYS"].apply(lambda x: dt.now() + timedelta(x))
        df = df.sort_values(by=["DAYS"])
        df = df.round(2)
        return df

    def get_stock_positions(self):
        """
        Get all open Stocks first from Accounts API and later pricing information
        for the symbol via Qouotes
        """

        positions = self.positions

        # Filter for stocks
        options = ["EQUITY", "MUTUAL_FUND"]
        is_equity = positions["instrument_type"].isin(options)
        df = positions[is_equity]

        if not df.empty:
            #  Retain only the columns needed and rename
            df = df[self.params_stocks.keys()]
            df["NET"] = df["quantity"] * (df["mark"] - df["averagePrice"])
            df.rename(columns=self.params_stocks, inplace=True)

        df = df.round(2)
        return df


def add_prices(df):
    """
    Get pricing info or the symbol via Quotes
    """

    try:
        quotes = Quotes()
        instruments = df["symbol"]
        res = quotes.get_quotesDF(instruments)
        res_filter = res[
            [
                "symbol",
                "underlyingPrice",
                "strikePrice",
                "mark",
                "theta",
                "delta",
                "daysToExpiration",
            ]
        ]
        # For Money Market Funds
        res_filter.loc[:, "mark"] = res_filter["mark"].fillna(1)
        merged_df = pd.merge(df, res_filter, on="symbol")
        return merged_df
    except Exception as e:
        logging.error(f"Error fetching prices: {str(e)}")
        return pd.DataFrame()


def get_account():
    """
    Get open positions and balances for a given account

    Args:
        field (str, optional): positions or balances. Defaults to 'positions'.

    Returns:
        _type_: _description_
    """

    try:
        account = Account().get_portfolio(account=UserConfig.ACCOUNT_NUMBER)
        position_df = convert_to_df(account.positions)

        # Populate pricing for all tickers
        positions = add_prices(position_df)
        return positions, account.balance
    except Exception as e:
        logging.error(f"Error fetching account data: {str(e)}")
        return pd.DataFrame(), None
