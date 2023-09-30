import yfinance as yf


def get_stock_price(ticker, history=5):
    """
    Get historical stock price data for a given ticker symbol.

    Args:
        ticker (str): The ticker symbol of the stock.
        history (int): The number of years of historical data to retrieve (default is 5 years).

    Returns:
        str: A formatted string containing the historical stock price data.
    """
    stock = yf.Ticker(ticker)
    df = stock.history(period="1y")

    df = df[["Close", "Volume"]]
    df.index = [str(x).split()[0] for x in list(df.index)]
    df.index.rename("Date", inplace=True)

    df = df[-history:]

    return df.to_string()


def get_financial_statements(ticker):
    """
    Get the financial statements (balance sheet) for a given company's ticker symbol.

    Args:
        ticker (str): The ticker symbol of the company.

    Returns:
        str: A formatted string containing the financial statements (balance sheet) data.
    """
    company = yf.Ticker(ticker)
    balance_sheet = company.balance_sheet

    if balance_sheet.shape[1] >= 3:
        balance_sheet = balance_sheet.iloc[:, :3]

    balance_sheet = balance_sheet.dropna(how="any")

    return balance_sheet.to_string()
