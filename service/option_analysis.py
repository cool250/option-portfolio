from datetime import datetime as dt
from datetime import timedelta

from broker.option_chain import OptionChain
from broker.options import Options
from utils.enums import PUT_CALL

params = {
    "min_expiration_days": 15,
    "max_expiration_days": 45,
    "range": "OTM",
    "strategy": "SINGLE",
    "contractType" : "PUT"

}


def get_ticker_details(ticker: str):
    startDate = dt.now() + timedelta(days=params["min_expiration_days"])
    endDate = dt.now() + timedelta(days=params["max_expiration_days"])
    options = Options()
    option_chain_req = OptionChain(
        symbol=ticker,
        strategy=params["strategy"],
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

    # Get expiration weeks
    expiration_week_dict = res[mapKey]
    expiration_week = [key for key in expiration_week_dict]
    weeks_choice =[{"label": i, "value": i} for i in expiration_week]

    return current_stock_price, weeks_choice
