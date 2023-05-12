import logging

import numpy as np
import pandas as pd

from broker.account import Account
from broker.config import ACCOUNT_NUMBER
from broker.quotes import Quotes
from utils.enums import PUT_CALL
from utils.functions import formatter_number_2_digits, formatter_percent


class AccountPositions:
    def __init__(self):
        super().__init__()
        self.params_options = {
            "quantity": "QTY",
            "underlying": "TICKER",
            "symbol": "SYMBOL",
            "underlyingPrice": "TICKER PRICE",
            "strikePrice": "STRIKE PRICE",
            "lastPrice": "CURRENT PRICE",
            "intrinsic": "INTRINSIC",
            "extrinsic": "EXTRINSIC",
            "ITM": "ITM",
            "theta": "THETA",
            "averagePrice": "PURCHASE PRICE",
            "daysToExpiration": "DAYS",
            "maintenanceRequirement": "MARGIN",
        }

        self.params_stocks = {
            "quantity": "QTY",
            "underlying": "TICKER",
            "mark": "TICKER PRICE",
            "averagePrice": "AVG PRICE",
            "total": "TOTAL",
            "maintenanceRequirement": "MARGIN",
        }

        # Get All Open Positions
        self.res = pd.DataFrame()

    def get_put_positions(self):
        """
        Get all open Puts first from Accounts API and later pricing information
        for the symbol via Quotes
        """

        def addmoneyness(row):
            intrinsic = round(max(row["strikePrice"] - row["underlyingPrice"], 0), 2)
            extrinsic = round(row["lastPrice"] - intrinsic, 2)
            itm = np.where(row["strikePrice"] > row["underlyingPrice"], "Y", "N")
            return intrinsic, extrinsic, itm

        res = self.get_account_positions()
        # Filter for puts
        is_put = res["option_type"] == PUT_CALL.PUT.value
        res_puts = res[is_put]

        # Get Quotes for open puts
        df = self.__get_option_pricing(res_puts)

        res_df = pd.DataFrame()
        res_df[["intrinsic", "extrinsic", "ITM"]] = df.apply(
            addmoneyness, axis=1, result_type="expand"
        )
        df = df.join(res_df)

        if not df.empty:
            df = df.drop(
                ["option_type", "instrument_type", "intrinsic", "extrinsic"], axis=1
            )
            df = df.rename(columns=self.params_options)

        # Add liquidity for Puts if assigned
        df["COST"] = df["STRIKE PRICE"] * df["QTY"].abs() * 100
        df["RETURNS"] = (
            (
                (
                    df["CURRENT PRICE"]
                    * 365
                    * df["QTY"]
                    / (df["MARGIN"] * df["DAYS"])
                    * 100
                )
            )
            .abs()
            .apply(formatter_percent)
        )

        return df

    def get_call_positions(self):
        """
        Get all open Calls first from Accounts API and later pricing information
        for the symbol via Qouotes
        """

        def addmoneyness(row):
            intrinsic = round(max(row["underlyingPrice"] - row["strikePrice"], 0), 2)
            extrinsic = round(row["lastPrice"] - intrinsic, 2)
            itm = np.where(row["strikePrice"] < row["underlyingPrice"], "Y", "N")
            return intrinsic, extrinsic, itm

        res = self.get_account_positions()

        # Filter for calls
        is_call = res["option_type"] == PUT_CALL.CALL.value
        res_calls = res[is_call]

        # Get Quotes for open calls
        df = self.__get_option_pricing(res_calls)

        res_df = pd.DataFrame()
        res_df[["intrinsic", "extrinsic", "ITM"]] = df.apply(
            addmoneyness, axis=1, result_type="expand"
        )
        df = df.join(res_df)

        if not df.empty:
            df = df.drop(["option_type", "instrument_type"], axis=1)
            df = df.rename(columns=self.params_options)

        return df

    def get_stock_positions(self):
        """
        Get all open Stocks first from Accounts API and later pricing information
        for the symbol via Qouotes
        """

        res = self.get_account_positions()

        # Filter for calls
        is_equity = res["instrument_type"] == "EQUITY"
        res_equity = res[is_equity]

        # Get Quotes for open calls
        df = self.__get_stock_pricing(res_equity)
        if not df.empty:
            df = df.drop(["option_type", "instrument_type", "symbol"], axis=1)
            df["total"] = (df["quantity"] * df["averagePrice"]).apply(
                formatter_number_2_digits
            )
            df = df.rename(columns=self.params_stocks)
        return df

    def get_account_positions(self):
        """
        Get open positions for a given account
        """

        if self.res.empty:
            account = Account()
            logging.debug(" Getting positions")
            self.res = account.get_positionsDF(account=ACCOUNT_NUMBER)

        return self.res

    def __get_option_pricing(self, df):
        """
        Get pricing info or the symbol via Quotes
        """

        def get_quotes(row):
            """
            Invoke quotes for passed symbol
            """

            quotes = Quotes()
            res = quotes.get_quotes(row["symbol"])
            return res

        # Invoke getQuotesForSymbol for each symbol
        res = df.apply(get_quotes, axis=1, result_type="expand")

        res = res[
            ["underlyingPrice", "strikePrice", "lastPrice", "theta", "daysToExpiration"]
        ]
        res["theta"] = res["theta"].apply(formatter_number_2_digits)
        df = df.join(res)
        return df

    def __get_stock_pricing(self, df):
        """
        Get pricing info or the symbol via Quotes
        """

        def get_quotes(row):
            """
            Invoke quotes for passed symbol
            """

            quotes = Quotes()
            res = quotes.get_quotes(row["symbol"])
            return res["mark"]

        # Invoke getQuotesForSymbol for each symbol
        res = pd.DataFrame()
        res["mark"] = df.apply(get_quotes, axis=1)
        df = df.join(res)
        return df
