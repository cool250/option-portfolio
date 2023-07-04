import re
from datetime import datetime as dt
import pandas as pd

# Define Formatters
def formatter_currency(x):
    return "${:,.0f}".format(x) if x >= 0 else "(${:,.0f})".format(abs(x))


def formatter_currency_with_cents(x):
    return "${:,.2f}".format(x) if x >= 0 else "(${:,.2f})".format(abs(x))


def formatter_percent(x):
    x = 100 * x
    return "{:,.1f}%".format(x) if x >= 0 else "({:,.1f}%)".format(abs(x))


def formatter_percent_2_digits(x):
    x = 100 * x
    return "{:,.2f}%".format(x) if x >= 0 else "({:,.2f}%)".format(abs(x))


def formatter_number(x):
    return "{:,.0f}".format(x) if x >= 0 else "({:,.0f})".format(abs(x))


def formatter_number_2_digits(x):
    return "{:,.2f}".format(x) if x >= 0 else "({:,.2f})".format(abs(x))

def change_date_format(date_to_convert):
    return dt.strptime(date_to_convert, '%Y-%m-%d').strftime('%m/%d/%y')

def date_from_milliseconds(x):
    return dt.fromtimestamp(x / 1000.0).strftime("%Y-%m-%d")

def convert_to_df(list_obj):
    return pd.DataFrame([vars(s) for s in list_obj])

def parse_option_symbol(symbol):
    # Regex to parse option string
    matcher = re.compile(r'^(.+)([0-9]{6})([PC])(\d*\.?\d*)')

    groups = matcher.search(symbol)

    # Date is in group 2
    date_string = groups[2]

    # Strike is in group 4
    strike_price = groups[4]

    # Convert to datetime
    expiration_date = dt.strptime(date_string, '%m%d%y').strftime('%Y-%m-%d')

    return expiration_date, strike_price
