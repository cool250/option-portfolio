from datetime import datetime as dt
from datetime import timedelta
import pandas as pd
import traceback

from broker.option import Option
from broker.option_chain import OptionChain
from broker.options import Options
from utils.enums import PUT_CALL
from utils.functions import formatter_currency, formatter_percent


def income_finder(ticker, **kwargs):
    """ 
    Get option chain for a given ticker
    """

    # define the parameters that we will take when a new object is initalized.
    params = {
        "min_expiration_days": 15,
        "max_expiration_days": 45,
        "moneyness": 5,
        "premium": 2,
        "contractType": None,
        "volatility": None,
        "min_delta": 0.25,
        "max_delta": 0.35,
        "strategy": "SINGLE",
        "interval": 1,
        "range": "OTM"
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
        strategy=params["strategy"],
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

            option = Option()
            option.symbol = strike_detail["symbol"]
            option.underlying = ticker
            option.mark = float(strike_detail["mark"])
            option.delta = strike_detail["delta"]
            option.volatility = strike_detail["volatility"]
            option.expiration_type = strike_detail["expirationType"]
            option.expiration = expiration_week[0]
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
            #option.open_interest = int(strike_detail["openInterest"])
            #option.volume = int(strike_detail["totalVolume"])
            option.percentage_otm = formatter_percent((option.stock_price - option.strike_price) /option.stock_price)

            option.spread = float(strike_detail["ask"]) - float(strike_detail["bid"])
            option.desired_premium = float(params["premium"])
            option.desired_moneyness = float(params["moneyness"])
            option.desired_min_delta = float(params["min_delta"])
            option.desired_max_delta = float(params["max_delta"])

            # Append to the list
            option_chain.append(option)
    strikes_list = filter(filter_strikes, option_chain)
    df = pd.DataFrame([vars(s) for s in strikes_list])
    return df


def filter_strikes(option):
    """ 
    Filter out strikes not matching filter criteria in screener
    """

    def moneyness_flag(option):
        return (
            (option.type == PUT_CALL.PUT.value)
            and (
                option.strike_price
                <= (1 - option.desired_moneyness / 100) * option.stock_price
            )
            or (
                (option.type == PUT_CALL.CALL.value)
                and (
                    option.strike_price
                    >= (1 + option.desired_moneyness / 100) * option.stock_price
                )
            )
        )

    def premium_flag(option):
        return option.mark > option.desired_premium * option.stock_price / 100

    def delta_flag(option):
        """
        Since UI is taking positive deltas, need to convert to negative deltas for puts
        """

        return (
            (option.type == PUT_CALL.PUT.value)
            and (-option.desired_min_delta > option.delta > -option.desired_max_delta)
            or (
                (option.type == PUT_CALL.CALL.value)
                and (option.desired_min_delta < option.delta < option.desired_max_delta)
            )
        )
    try:
        if premium_flag(option) and moneyness_flag(option) and delta_flag(option):
            return True
        else:
            return False
    except:
        return False
