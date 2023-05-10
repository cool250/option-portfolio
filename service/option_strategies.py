import multiprocessing

import pandas as pd
from joblib import Parallel, delayed

from utils.enums import ORDER_TYPE, PUT_CALL
from utils.functions import formatter_currency_with_cents

from .checks import singles_checks
from .search_income import income_finder

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
    "volume" : "VOLUME",
    "percentage_otm" : "OTM",
}

def search_options(ticker, params):
    return income_finder(ticker,**params)


def watchlist_income(watch_list, params):
    df = pd.DataFrame()

    # Get Option chain for watch list
    # Parallel mode for API calls
    results = Parallel(n_jobs=num_cores)(delayed(search_options)(i, params) for i in watch_list)

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
                "desired_premium",
                "desired_moneyness",
                "desired_min_delta",
                "desired_max_delta",
                "type",
                "expiration_type",
                "spread",
                "expiration"
            ],
            axis=1,
        )

        df = df.rename(columns=TABLE_MAPPING)
    return df
