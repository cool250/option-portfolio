from datetime import datetime as dt
from datetime import timedelta
import pandas as pd

from broker.option import Option
from broker.option_chain import OptionChain
from broker.options import Options
from utils.enums import PUT_CALL
from utils.functions import formatter_percent, formatter_currency_with_cents
import multiprocessing

import pandas as pd
from joblib import Parallel, delayed

num_cores = multiprocessing.cpu_count()

# Mapping column for UI display
TABLE_MAPPING = {
    "strike_price": "STRIKE",
    "stock_price": "STOCK PRICE",
    "volatility": "VOLATILITY",
    "delta": "DELTA",
    "mark": "MARK",
    "underlying": "TICKER",
    "expiration": "EXPIRATION",
    "days_to_expiration": "DAYS",
    "returns": "RETURNS",
    "breakeven": "BREAK EVEN",
    "symbol": "SYMBOL",
    "open_interest": "OPEN INT",
    "volume": "VOLUME",
    "percentage_otm": "OTM",
}


def income_finder(ticker: str, **kwargs) -> pd.DataFrame:
    """
    Get option chain for a given ticker
    """

    # define the parameters that we will take when a new object is initalized.
    params = {
        "min_expiration_days": 15,
        "max_expiration_days": 45,
        "moneyness": 2,
        "premium": 1,
        "contractType": None,
        "volatility": None,
        "min_delta": 0.25,
        "max_delta": 0.35,
        "tran_type": "SINGLE",
        "interval": 1,
        "range": "OTM",
    }

    for key in kwargs:
        if key not in params:
            print("WARNING: The argument, {} is an unknown argument.".format(key))
            raise KeyError("Invalid Argument Name.")

    params.update(kwargs.items())

    if not ticker:
        raise ValueError(" Ticker must be provided")

    if not params["contractType"]:
        raise ValueError(" Contract Type of either PUT or CALL should be provided")

    startDate = dt.now() + timedelta(days=params["min_expiration_days"])
    endDate = dt.now() + timedelta(days=params["max_expiration_days"])

    options = Options()
    option_chain_req = OptionChain(
        symbol=ticker,
        strategy="SINGLE",
        contractType=params["contractType"],
        fromDate=startDate,
        toDate=endDate,
        range=params["range"],
    )

    # API call
    res = options.get_options_chain(option_chain=option_chain_req)

    # Current Stock Price
    current_stock_price = res["underlyingPrice"]

    # Use Put or Call key to parse JSON response
    if params["contractType"] == PUT_CALL.PUT.value:
        mapKey = "putExpDateMap"
    elif params["contractType"] == PUT_CALL.CALL.value:
        mapKey = "callExpDateMap"

    # Get expiration periods
    expiration_weeks = res[mapKey].items()

    # Parse the Put response. TD option chain JSON is nested
    option_chain = []

    # Iterate all the expiration weeks
    for expiration_week in expiration_weeks:
        # Details for a given week's strikes
        strikes = expiration_week[1].items()
        for strike in strikes:
            strike_price = strike[0]  # Get the strike price
            # Get the option chain detail for that strike price
            # avaialble as first element of tuple object
            strike_detail = (strike[1])[0]

            option = populate_option(
                ticker, params, current_stock_price, expiration_week, strike_detail
            )

            # Append to the list if pass the filter criteria
            if filter_strikes(option, params):
                option_chain.append(option)
    df = pd.DataFrame([vars(s) for s in option_chain])
    return df


def populate_option(
    ticker, params, current_stock_price, expiration_week, strike_detail
):
    option = Option()
    option.symbol = strike_detail["symbol"]
    option.underlying = ticker
    option.mark = float(strike_detail["mark"])
    option.strike_price = float(strike_detail["strikePrice"])
    option.type = strike_detail["putCall"]
    option.days_to_expiration = strike_detail["daysToExpiration"]
    option.returns = formatter_percent(
        365
        * option.mark
        / ((option.strike_price - option.mark) * option.days_to_expiration)
    )

    # breakeven logic
    if params["contractType"] == PUT_CALL.PUT.value:
        option.breakeven = option.strike_price - option.mark
    elif params["contractType"] == PUT_CALL.CALL.value:
        option.breakeven = option.strike_price + option.mark

    option.stock_price = float(current_stock_price)
    option.delta = strike_detail["delta"]
    option.volatility = strike_detail["volatility"]
    option.percentage_otm = formatter_percent(
        (option.stock_price - option.strike_price) / option.stock_price
    )
    return option


def filter_strikes(option: Option, params) -> bool:
    """
    Filter out strikes not matching filter criteria in screener
    """

    desired_premium = float(params["premium"])
    desired_moneyness = float(params["moneyness"])
    desired_min_delta = float(params["min_delta"])
    desired_max_delta = float(params["max_delta"])

    def moneyness_flag():
        return (
            (option.type == PUT_CALL.PUT.value)
            and (
                option.strike_price
                <= (1 - desired_moneyness / 100) * option.stock_price
            )
            or (
                (option.type == PUT_CALL.CALL.value)
                and (
                    option.strike_price
                    >= (1 + desired_moneyness / 100) * option.stock_price
                )
            )
        )

    def premium_flag():
        return option.mark > desired_premium * option.stock_price / 100

    def delta_flag():
        """
        Since UI is taking positive deltas, need to convert to negative deltas for puts
        """

        return (
            (option.type == PUT_CALL.PUT.value)
            and (-desired_min_delta > option.delta > -desired_max_delta)
            or (
                (option.type == PUT_CALL.CALL.value)
                and (desired_min_delta < option.delta < desired_max_delta)
            )
        )

    try:
        if premium_flag() and moneyness_flag() and delta_flag():
            return True
        else:
            return False
    except:
        return False


def watchlist_income(watch_list: list, params: dict) -> pd.DataFrame:
    """Invoke the Options API in parallel for requested stocks and filter parameters

    Args:
        watch_list (list): _description_
        params (dict): _description_

    Returns:
        pd.DataFrame: _description_
    """
    df = pd.DataFrame()

    # Get Option chain for watch list
    # Parallel mode for API calls
    results = Parallel(n_jobs=num_cores)(
        delayed(income_finder)(i, **params) for i in watch_list
    )

    #  Aggregate the results
    for result in results:
        df = pd.concat([df, result], ignore_index=True)

    if not df.empty:
        df = df.sort_values(by=["returns"], ascending=False)
        df["strike_price"] = df["strike_price"].apply(formatter_currency_with_cents)
        df["stock_price"] = df["stock_price"].apply(formatter_currency_with_cents)
        df["mark"] = df["mark"].apply(formatter_currency_with_cents)
        df["breakeven"] = df["breakeven"].apply(formatter_currency_with_cents)

        df = df.drop(
            [
                "type",
            ],
            axis=1,
        )

        df = df.rename(columns=TABLE_MAPPING)
    return df
