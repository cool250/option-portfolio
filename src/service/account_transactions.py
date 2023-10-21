import logging
from datetime import datetime as dt
from datetime import timedelta

import numpy as np
import pandas as pd
from pandas.tseries.offsets import CustomBusinessDay

from broker.transactions import Transaction
from config.user_config import UserConfig
from utils.constants import DATE_FORMAT, TIMESTAMP_FORMAT
from utils.functions import parse_option_symbol
from utils.ustradingcalendar import USTradingCalendar

default_start_duration = 180
cal = USTradingCalendar()


# Mapping column for easier handling
params = {
    "transactionDate": "DATE",
    "netAmount": "TOTAL_PRICE",
    "transactionSubType": "TRAN_TYPE",
    "transactionItem.amount": "QTY",
    "transactionItem.price": "PRICE",
    "transactionItem.instrument.underlyingSymbol": "TICKER",
    "transactionItem.instrument.assetType": "TYPE",
    "transactionItem.instrument.optionExpirationDate": "EXPIRY_DATE",
    "transactionItem.instrument.putCall": "OPTION_TYPE",
    "transactionItem.positionEffect": "POSITION",
    "transactionItem.instrument.symbol": "SYMBOL",
    "transactionItem.instruction": "INSTRUCTION",
}


def get_report(
    start_close_date=None,
    end_close_date=None,
    symbol=None,
    instrument_type=None,
    status="All",
):
    """
    This method is called from Reports screen.
    It will internally call get_transactions method.

    Args:
        start_date ([str], optional): [Include Transcations after the start date]. Defaults to None.
        end_date ([str], optional): [Include Transcations before the end date]. Defaults to None.
        symbol ([str], optional): [description]. Defaults to None.
        instrument_type ([str], optional): [description]. Defaults to None.

    Returns:
        [df]: [Transactions for given search criteria]
    """
    # In case start date or end date is not passed, use to initialize default
    today = dt.now()
    if not start_close_date:
        start_close_date = today.strftime(DATE_FORMAT)

    if not end_close_date:
        end_close_date = today.strftime(DATE_FORMAT)

    df = get_api_transactions(start_close_date, end_close_date, symbol)
    if not df.empty:
        df = df.rename(columns=params)

        # Change df['transactionDate'] string to remove timestamp
        df["DATE"] = pd.to_datetime(df["DATE"], format=TIMESTAMP_FORMAT).dt.strftime(
            DATE_FORMAT
        )

        # Change df['optionExpirationDate'] string to remove timestamp
        df["EXPIRY_DATE"] = pd.to_datetime(
            df["EXPIRY_DATE"],
            format=TIMESTAMP_FORMAT,
        ).dt.strftime(DATE_FORMAT)

        # Lambda function to filter records based on closing date search input
        filter_date = lambda df: df[
            (df["DATE"] >= start_close_date) & (df["DATE"] <= end_close_date)
        ]

        if instrument_type == "PUT" or instrument_type == "CALL":
            df = parse_option_response(df, instrument_type)
            if not df.empty:
                df = filter_date(df)
                if status != "All":
                    df = df[df["STATUS"] == status]

        elif instrument_type == "EQUITY":
            # Filter for EQUITY
            df = parse_equity_response(df, instrument_type)
            df = df[(df["DATE"] >= start_close_date)]

        # For all options parse puts and calls independently and concat
        else:
            df_puts = parse_option_response(df, "PUT")
            df_calls = parse_option_response(df, "CALL")
            df = pd.concat([df_puts, df_calls])
            if not df.empty:
                df = filter_date(df)
                if status != "All":
                    df = df[df["STATUS"] == status]
        if not df.empty:
            df = df.sort_values(by=["CLOSE_DATE"])
        df = df.round(2)

    return df


def get_api_transactions(
    start_close_date=None,
    end_close_date=None,
    symbol=None,
):
    # Modify start date to use 45 days in advance to get all options expiring before entered start date
    # The API takes trade open date as start date not trade closing
    search_start_date = (
        dt.strptime(start_close_date, DATE_FORMAT) - timedelta(days=45)
    ).strftime(DATE_FORMAT)

    delta = dt.strptime(end_close_date, DATE_FORMAT) - dt.strptime(
        search_start_date, DATE_FORMAT
    )

    logging.info(f" Report Search Duration {delta.days} days")
    if delta.days < 365:
        transaction = Transaction()
        df = transaction.get_transactionsDF(
            UserConfig.ACCOUNT_NUMBER,
            transaction_type="TRADE",
            symbol=symbol,
            start_date=search_start_date,
            end_date=end_close_date,
        )
        return df
    else:
        raise ValueError(" Start and end date duration should less than 320 days")


def parse_option_response(df, instrument_type):
    """
    [Parse Option Response coming from transactions API]

    Args:
        df:  [Filtered Options transaction]
        instrument_type:

    Returns:
        [df]: [Options transactions to be displayed on screen]
    """
    # PUT or CALL option types
    df_options = df[df["OPTION_TYPE"] == instrument_type]

    # Get assigned equities to remove option income for option assignments
    # For short Put option assigment - OA is of type "BUY", short call - OA is of type "SELL"
    if instrument_type == "PUT":
        instruction = "BUY"
    else:
        instruction = "SELL"

    # Stock transactions due to corresponding options Assignment
    df_assigned_stocks = get_assigned_stock(df, instruction)

    # Aggregate function to combine orders which might have been split by broker into multiple orders while execution
    aggregate_function = {
        "DATE": "first",
        "EXPIRY_DATE": "first",
        "TICKER": "first",
        "INSTRUCTION": "first",
        "TOTAL_PRICE": "sum",
        "PRICE": "mean",
        "QTY": "sum",
    }

    # All opening positions
    df_open = df_options[df_options["POSITION"] == "OPENING"]

    # Combine open orders if needed
    df_open = df_open.groupby(["SYMBOL"]).agg(aggregate_function)
    df_open = df_open.reset_index()

    # All Closing positions ( for rolled trades)
    df_close = df_options[df_options["POSITION"] == "CLOSING"]

    # Combine closed orders if needed
    df_close = df_close.groupby(["SYMBOL"]).agg(aggregate_function)
    df_close = df_close.reset_index()

    # Merge option opening transaction with stock assignment or closing transaction
    # For expired transaction there is no corresponding closing or assignment.
    oa_df = merge_openclose(df_open, df_close, df_assigned_stocks)

    if oa_df.empty:
        return oa_df
    else:
        # Calculate profits by subtracting closing costs from opening
        final_df = calculate_final_payoff(oa_df)
        # Add timestamp and sort using expiry date
        return final_df


def merge_openclose(df_open, df_close, df_assigned):
    """Merge opening and closing postions.
    For rolled trades, corresponding df_close is present
    For assigned stock, corresponding df_assigned_stocks is present
    For Active or Expired trades no closing positions

    Args:
        df_open (_type_): _description_
        df_close (_type_): _description_
        df_assigned_stocks (_type_): _description_

    Returns:
        _type_: _description_
    """

    # Merge opening and closing trades
    df_options = pd.merge(
        df_open,
        df_close,
        how="outer",
        on=["SYMBOL", "QTY", "TICKER"],
        suffixes=(None, "_C"),
    )

    # Match transactions where assignment happened earlier than option expiry date
    df_adjusted_assigned = handle_early_assignment(df_options, df_assigned)

    # Merge assigned stock positions using options symbol. Earlier merge added option symbol for assigned df
    oa_df = pd.merge(
        df_options,
        df_adjusted_assigned,
        how="left",
        on=["SYMBOL"],
        suffixes=(None, "_E"),
    )

    return oa_df


def handle_early_assignment(df_options, df_assigned):
    """Handle expiry dates of early assignment to match open trade expiry date
    We try to match open trades that don't have a closing trade with the assigned stock when
    QTY and ticker matches. This allows us to tag option trades that were assigned early

    Args:
        df_options (_type_): _description_
        df_assigned (_type_): _description_

    Returns:
        _type_: _description_
    """
    # All option trades that don't have any closing option trades
    df_option_openonly = df_options[df_options["PRICE_C"].isna()]

    # Create a copy to avoid pandas warning when adding new column later to filtered Dataframes
    df_option_open = df_option_openonly.copy()
    df_assigned = df_assigned.copy()

    # Add timestamp and sort for merge asof operation using closest timestamp
    df_option_open["EXPIRY_DATE_TS"] = pd.to_datetime(df_option_open["EXPIRY_DATE"])
    df_assigned["EXPIRY_DATE_TS"] = pd.to_datetime(df_assigned["EXPIRY_DATE"])

    df_option_open = df_option_open.sort_values(by=["EXPIRY_DATE_TS"])
    df_assigned = df_assigned.sort_values(by=["EXPIRY_DATE_TS"])

    # Adjust stock assignments date to match opening expiration date for early assignments if needed
    # Do not add suffix to options df for merge later
    df_adjusted_assigned = pd.merge_asof(
        df_assigned,
        df_option_open,
        on="EXPIRY_DATE_TS",
        by=["QTY", "TICKER"],
        allow_exact_matches=True,
        direction="nearest",
        tolerance=pd.Timedelta("30days"),
        suffixes=("_A", None),
    )

    return df_adjusted_assigned


def get_assigned_stock(df, instruction):
    """
    Get assigned stocks and modify qty, ticker, and expiry date to merge with corresponding option transaction
    Args:
        df:
        instruction:

    Returns:

    """
    df_assigned_stocks = df[
        (df["TRAN_TYPE"] == "OA") & (df["INSTRUCTION"] == instruction)
    ]
    df_assigned_stocks.loc[:, "QTY"] = df_assigned_stocks.QTY / 100
    df_assigned_stocks.loc[:, "TICKER"] = df_assigned_stocks.SYMBOL
    df_assigned_stocks.loc[:, "EXPIRY_DATE"] = df_assigned_stocks["DATE"].apply(
        get_previous_bdate
    )

    return df_assigned_stocks


def calculate_final_payoff(result_df):
    """Calculates the trade profit ( open trade - close trade)

    Args:
        result_df (DataFrame): Input dataframe

    Returns:
        DataFrame:  DF with Total Price and Status for each trade
    """

    result_df[["DATE", "CLOSE_DATE"]] = result_df.apply(
        get_date, axis=1, result_type="expand"
    )
    result_df["PRICE"] = result_df["PRICE"].fillna(0)
    result_df["CLOSE_PRICE"] = result_df["PRICE_C"].fillna(0)

    # Handle assigned options by adding Close Price as Open price since profit = 0
    result_df.CLOSE_PRICE = np.where(
        (result_df.TRAN_TYPE == "OA"), result_df.PRICE, result_df.CLOSE_PRICE
    )

    result_df["TOTAL_PRICE"] = result_df.apply(get_net_total_price, axis=1)
    result_df["STATUS"] = result_df.apply(get_transaction_status, axis=1)
    # Add Close Date if missing and Strike price by parsing option symbol string
    result_df[["CLOSE_DATE", "STRIKE_PRICE"]] = result_df.apply(
        parse_option_string, axis=1, result_type="expand"
    )

    return result_df


def get_net_total_price(row):
    """Calculate net price for each trade row

    Args:
        row ([df row]): [Single row of DF to whch the function is applied]

    Returns:
        [Net Total price]: [Sum of opening transcation and Closing transaction or 0 for assigned positions]
    """
    # Assigned option transaction don't have any profit
    tran_type = row["TRAN_TYPE"]
    if tran_type == "OA":
        return 0

    open_total = row["TOTAL_PRICE"]
    close_total = row["TOTAL_PRICE_C"]
    if pd.isna(open_total):
        open_total = 0
    if pd.isna(close_total):
        close_total = 0

    return open_total + close_total


def get_transaction_status(row):
    """Assign transcation status for each row

    Args:
        row ([df row]): [Single row of DF to whch the function is applied]

    Returns:
        Trade Status:Assigned, Rolled, Expired or Active status
    """
    if row.CLOSE_PRICE == row.PRICE:
        return "Assigned"
    elif row.CLOSE_PRICE > 0:
        return "Closed"
    elif row.CLOSE_PRICE == 0 and row.EXPIRY_DATE < dt.now().strftime(DATE_FORMAT):
        return "Expired"
    else:
        return "Active"


def parse_option_string(row):
    """Parse Option String to get expiration date and Strike price.
    If closing transaction is not applicable, use Expiry date as the Close date for those Option trades

    Args:
        row ([df row]): [Single row of DF to whch the function is applied]

    Returns:
        [type]: [description]
    """
    # Initialize
    strike_price = 0
    expiration_date = row["EXPIRY_DATE"]

    option_symbol = row["SYMBOL"]
    close_date = row["CLOSE_DATE"]
    if pd.notna(option_symbol):
        expiration_date, strike_price = parse_option_symbol(option_symbol)

    # If transaction was not explicitly closed, close date is same as option expiry date
    if pd.isna(close_date) and expiration_date:
        close_date = expiration_date
    return close_date, strike_price


def get_date(row):
    """Return dates for opening trade and Closing Trade for the Option Trade
    If Open Trade date is not pulled in the search criteria, the corresponding close trade is displayed
    on its own as independent Open Trade so swap with Open date for such trades

    Args:
        row ([df row]): [Single row of DF to whch the function is applied]

    Returns:
        [type]: [description]
    """

    open_date = row["DATE"]
    if pd.notna(row["DATE_C"]):
        close_date = row["DATE_C"]
    elif pd.notna(row["DATE_A"]):
        close_date = row["DATE_A"]
    else:
        close_date = None

    if pd.isna(open_date):
        # Open date is before Search and transaction not pulled or other mismatch
        # Only for closing transaction not matching
        open_date = close_date
        close_date = None
    return open_date, close_date


def get_previous_bdate(date):
    """gets previous businessdate based on US trading calendar

    Args:
        date (_type_): _description_

    Returns:
        _type_: _description_
    """
    previous_business_date = (
        dt.strptime(date, "%Y-%m-%d") - CustomBusinessDay(1, calendar=cal)
    ).strftime("%Y-%m-%d")
    return previous_business_date


def parse_equity_response(df, instrument_type):
    """[Parse Equity Response coming from transactions API]

    Args:
        df ([df]): [Filtered Options transaction]
        instrument_type: Equities, Options, etc.

    Returns:
        [df]: [Equity transactions to be displayed on screen]
    """

    # Filter for either Equity transactions
    df_equities = df[df["TYPE"] == instrument_type]

    return df_equities
