
import numpy as np
import pandas as pd

from broker.account import Account
from broker.config import ACCOUNT_NUMBER
from broker.quotes import Quotes
from utils.enums import PUT_CALL
from utils.functions import formatter_number_2_digits, formatter_percent, convert_to_df

class AccountPositions:
    def __init__(self):
        super().__init__()
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

        # Get All Open Positions
        self.securities_account = None
        self.positions = pd.DataFrame()

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

        res = self.get_account()
        # Filter for puts
        is_put = res["option_type"] == PUT_CALL.PUT.value
        df = res[is_put]

        res_df = pd.DataFrame()
        res_df[["intrinsic", "extrinsic", "ITM"]] = df.apply(
            addmoneyness, axis=1, result_type="expand"
        )
        df = df.join(res_df)

        if not df.empty:
            #  Retain only the columns needed and rename
            df = df[self.params_options.keys()]
            df["theta"] = df["theta"] * df["quantity"] * 100
            df["theta"] = df["theta"].apply(formatter_number_2_digits)
            df["delta"] = df["delta"] * df["quantity"] * 100
            df["delta"] = df["delta"].apply(formatter_number_2_digits)
            df.rename(columns=self.params_options, inplace=True)

        # Add liquidity for Puts if assigned
        df["COST"] = df["STRIKE PRICE"] * df["QTY"].abs() * 100
        df["RETURNS"] = (
            (
                (
                    (df["MARK"] * 365 * df["QTY"] * 100)
                    / (df["MARGIN"] * df["DAYS"])
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
            extrinsic = round(row["mark"] - intrinsic, 2)
            itm = np.where(row["strikePrice"] < row["underlyingPrice"], "Y", "N")
            return intrinsic, extrinsic, itm

        res = self.get_account()

        # Filter for calls
        is_call = res["option_type"] == PUT_CALL.CALL.value
        df = res[is_call]

        res_df = pd.DataFrame()
        res_df[["intrinsic", "extrinsic", "ITM"]] = df.apply(
            addmoneyness, axis=1, result_type="expand"
        )
        df = df.join(res_df)

        if not df.empty:
            #  Retain only the columns needed and rename
            df = df[self.params_options.keys()]
            df["theta"] = df["theta"] * df["quantity"] * 100
            df["theta"] = df["theta"].apply(formatter_number_2_digits)
            df["delta"] = df["delta"] * df["quantity"] * 100
            df["delta"] = df["delta"].apply(formatter_number_2_digits)
            df.rename(columns=self.params_options, inplace=True)

        return df

    def get_stock_positions(self):
        """
        Get all open Stocks first from Accounts API and later pricing information
        for the symbol via Qouotes
        """

        res = self.get_account()

        # Filter for stocks
        options = ['EQUITY', 'MUTUAL_FUND']
        is_equity = res["instrument_type"].isin(options)
        df = res[is_equity]

        if not df.empty:
            #  Retain only the columns needed and rename
            df = df[self.params_stocks.keys()]
            # TODO: get an error "value is trying to be set on a copy of a slice from a DataFrame" when this line is before dropping columns
            df["NET"] = (df["quantity"] * (df["mark"] - df["averagePrice"])).apply(
                formatter_number_2_digits
            )
            df.rename(columns=self.params_stocks, inplace=True)
        return df

    def get_account(self, field='positions'):
        """
        Get open positions and balances for a given account
        
        Args:
            field (str, optional): positions or balances. Defaults to 'positions'.

        Returns:
            _type_: _description_
        """
        if self.securities_account is None:
            account = Account()
            self.securities_account = account.get_portfolio(account=ACCOUNT_NUMBER)
            position_df = convert_to_df(self.securities_account.positions)
            
            # Populate pricing for all tickers
            self.positions = self.__get_pricing(position_df)
        if field == 'balances':
            return self.securities_account.balance
        else:
            return self.positions
    
    def __get_pricing(self, df):
        """
        Get pricing info or the symbol via Quotes
        """

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
        res_filter.loc[:,'mark'] = res_filter['mark'].fillna(1)
        merged_df = pd.merge(df, res_filter, on="symbol")
        return merged_df