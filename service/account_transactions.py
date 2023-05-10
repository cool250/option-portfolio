from datetime import datetime as dt
from datetime import timedelta

import numpy as np
import pandas as pd
from pandas.tseries.offsets import CustomBusinessDay
import logging

from broker.config import ACCOUNT_NUMBER
from broker.transactions import Transaction
from utils.functions import parse_option_symbol
from utils.ustradingcalendar import USTradingCalendar

default_start_duration = 180
cal = USTradingCalendar()

# Mapping column for UI display
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


def get_transactions(
    start_date=None, end_date=None, symbol=None, instrument_type=None, tran_type=None
):
    """[Calls the TD transactions API class ]

    Args:
        start_date ([str], optional): [Include Transcations after the start date]. Defaults to None.
        end_date ([str], optional): [Include Transcations before the end date]. Defaults to None.
        symbol ([str], optional): [description]. Defaults to None.
        instrument_type ([str], optional): [description]. Defaults to None.
        tran_type ([str], optional): [description]. Defaults to None.

    Returns:
        df: Transactions for given search criteria
    """

    # In case start date or end date is not passed, use to initiliaze default
    to_date = dt.now()

    if not end_date:
        end_date = to_date.strftime("%Y-%m-%d")

    if not start_date:
        from_date = to_date - timedelta(days=default_start_duration)
        start_date = from_date.strftime("%Y-%m-%d")
    else:
        # Try to use 45 days in advance to get all options expiring before entered start date 
        start_date = (dt.strptime(start_date, "%Y-%m-%d") - timedelta(days=45)).strftime("%Y-%m-%d") 

    transaction = Transaction()
    df = transaction.get_transactionsDF(
        ACCOUNT_NUMBER,
        transaction_type="TRADE",
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
    )

    if not df.empty:

        # Change df['transactionDate'] string to remove timestamp
        df["transactionDate"] = pd.to_datetime(
            df["transactionDate"], format="%Y-%m-%dT%H:%M:%S%z"
        ).dt.strftime("%Y-%m-%d")

        # Change df['optionExpirationDate'] string to remove timestamp
        df["transactionItem.instrument.optionExpirationDate"] = pd.to_datetime(
            df["transactionItem.instrument.optionExpirationDate"], format="%Y-%m-%dT%H:%M:%S%z"
        ).dt.strftime("%Y-%m-%d")
    return df


def get_report(start_date=None, end_date=None, symbol=None, instrument_type=None):
    
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

    if not end_date:
        end_date = today.strftime("%Y-%m-%d")

    if not start_date:
        from_date = today - timedelta(days=default_start_duration)
        start_date = from_date.strftime("%Y-%m-%d")

    df = get_transactions(start_date, end_date, symbol, instrument_type)
 
    # Processing for Options
    if not df.empty:
        df = df.rename(columns=params)
        if instrument_type == "PUT" or instrument_type == "CALL" or instrument_type == "CALL":
            df = parse_option_response(df, instrument_type)

            # starting date of current year
            starting_day_of_current_year = dt.now().date().replace(month=1, day=1).strftime("%Y-%m-%d")
            
            #if close date is earlier than Jan 1st replace it to remove last year's closing records
            if start_date < starting_day_of_current_year:
                start_date = starting_day_of_current_year

            # Filter records based on closing date search input
            df = df[(df['CLOSE_DATE'] >= start_date) & (df['CLOSE_DATE'] <= end_date)]

        elif instrument_type == "EQUITY":
            # Filter for EQUITY
            df = parse_equity_response(df, instrument_type)
            df = df[(df['DATE'] >= start_date)]

    return df


def parse_option_response(df, instrument_type):
    """
    [Parse Option Response coming from transactions API]

    Args:
        df:  [Filtered Options transaction]
        instrument_type:

    Returns:
        [df]: [Options transactions to be displayed on screen]
    """    
    # Filter for either PUT or CALL option types
    df_options = df[df["OPTION_TYPE"] == instrument_type]

    # Get equities to remove option income for option assignments
    if instrument_type == "PUT":
        instruction = "BUY"
    else:
        instruction = "SELL"
    df_assigned_stocks = get_assigned_stock(df, instruction)

    # All opening positions
    df_open = df_options[df_options["POSITION"] == 'OPENING']
    

    # Edge case - Combine orders which were split by broker into multiple orders while execution
    df_open = df_open.groupby(['SYMBOL', 'DATE', 'EXPIRY_DATE', 'TICKER', 'INSTRUCTION'])\
        .agg({'TOTAL_PRICE':'sum','PRICE':'mean', 'QTY':'sum'})
    df_open = df_open.reset_index()

    # All Closing positions ( for rolled trades)
    df_close = df_options [df_options["POSITION"] == 'CLOSING']

    # Combine orders which were split by broker into multiple orders while execution
    df_close = df_close.groupby(['SYMBOL', 'DATE', 'EXPIRY_DATE', 'TICKER', 'INSTRUCTION'])\
        .agg({'TOTAL_PRICE': 'sum', 'PRICE': 'mean', 'QTY': 'sum'})
    df_close = df_close.reset_index()

    # Merge opening and closing trades
    result_df = pd.merge(df_open, df_close, how="outer", on=["SYMBOL", "QTY", "TICKER"], suffixes=(None, "_C"))

    # Merge assigned stock positions
    oa_df = pd.merge(result_df, df_assigned_stocks, how="left", on=["QTY", "TICKER", "EXPIRY_DATE"],
                     suffixes=(None, "_E"))

    # RARE: Merge with stocks can produce duplicates is same Ticker has multiple lots with same expiry date and qty
    # DATE_E added to account for earlier assignments and similar qty, ticker ( very rare )
    oa_df.drop_duplicates(subset=["SYMBOL", "QTY", "TICKER", "DATE", "DATE_E"], keep='last', inplace=True)

    final_df = calculate_final_payoff(oa_df)
    final_df = final_df.sort_values(by=['DATE'])


    return final_df


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


def get_assigned_stock(df, instruction):
    """
    Get assigned stocks and modify qty, ticker, and expiry date to merge with corresponding option transaction
    Args:
        df:
        instruction:

    Returns:

    """
    df_assigned_stocks = df[(df["TRAN_TYPE"] == "OA") & (df["INSTRUCTION"] == instruction)]
    df_assigned_stocks.loc[:,'QTY'] = df_assigned_stocks.QTY / 100
    df_assigned_stocks.loc[:,'TICKER'] = df_assigned_stocks.SYMBOL
    df_assigned_stocks.loc[:,'EXPIRY_DATE'] = df_assigned_stocks["DATE"].apply(get_previous_bdate)

    return df_assigned_stocks


def calculate_final_payoff(result_df):
    """Calculates the trade profit ( open trade - close trade)

    Args:
        result_df (DataFrame): Input dataframe 

    Returns:
        DataFrame:  DF with Total Price and Status for each trade
    """

    result_df[["DATE", "CLOSE_DATE"]] = result_df.apply(get_date, axis=1, result_type="expand")
    result_df["PRICE"] = result_df["PRICE"].fillna(0)
    result_df["CLOSE_PRICE"] = result_df["PRICE_C"].fillna(0)

    # Handle assigned options by adding Close Price as Open price since profit = 0
    result_df.CLOSE_PRICE = np.where((result_df.TRAN_TYPE == 'OA'),
                                     result_df.PRICE, result_df.CLOSE_PRICE)

    result_df["TOTAL_PRICE"] = result_df.apply(get_net_total_price, axis=1)
    result_df["STATUS"] = result_df.apply(get_transaction_status, axis=1)
    # Add Close Date if missing and Strike price by parsing option symbol string
    result_df[["CLOSE_DATE", "STRIKE_PRICE"]] = result_df.apply(parse_option_string, axis=1, result_type="expand")

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

    return round(open_total + close_total, 2)


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
        return "Rolled"
    elif row.CLOSE_PRICE == 0 and row.EXPIRY_DATE < dt.now().strftime("%Y-%m-%d"):
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
    if not pd.isna(option_symbol):
        expiration_date, strike_price = parse_option_symbol(option_symbol)

    # If transaction was not explicitly closed, close date is same as option expiry date
    if pd.isna(close_date) and expiration_date:
        close_date = expiration_date
    return close_date, strike_price


def get_date(row):
    """ Return dates for opening trade and Closing Trade for the Option Trade
    If Open Trade date is not pulled in the search criteria, the corresponding close trade is displayed
    on its own as independent Open Trade so swap with Open date for such trades 

    Args:
        row ([df row]): [Single row of DF to whch the function is applied]

    Returns:
        [type]: [description]
    """    

    open_date = row["DATE"]
    close_date = row["DATE_C"]

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
    previous_business_date = (dt.strptime(date, "%Y-%m-%d") - CustomBusinessDay(1, calendar=cal)).strftime("%Y-%m-%d")
    return previous_business_date



