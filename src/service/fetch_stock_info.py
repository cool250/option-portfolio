import logging

from utils.fetch_news import get_stock_news
from utils.finance import get_financial_statements, get_stock_price
from utils.openai import get_stock_ticker, stock_prediction


def analyze_stock(user_query):
    """
    Analyze a stock based on a user query.

    Args:
        user_query (str): The user query related to the stock analysis.

    Returns:
        str: Investment analysis and recommendation for the specified stock.
    """
    company_name, ticker = get_stock_ticker(user_query)
    logging.debug({"Query": user_query, "Company_name": company_name, "Ticker": ticker})
    stock_data = get_stock_price(ticker, history=10)
    stock_financials = get_financial_statements(ticker)
    stock_news = get_stock_news(company_name)

    available_information = f"Stock Price: {stock_data}\n\nStock Financials: {stock_financials}\n\nStock News: {stock_news}"
    context = f" You have the following information available about {company_name}, {available_information} \
            Write (4-6) pointwise investment analysis to answer user query.Try to give positives and negatives"

    return stock_prediction(context, user_query)
