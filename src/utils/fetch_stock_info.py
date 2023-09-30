import json
import re

import openai
import requests
import yfinance as yf
from bs4 import BeautifulSoup
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.prompts.chat import HumanMessage, SystemMessage

llm = ChatOpenAI()


# Fetch stock data from Yahoo Finance
def get_stock_price(ticker, history=5):
    stock = yf.Ticker(ticker)
    df = stock.history(period="1y")
    df = df[["Close", "Volume"]]
    df.index = [str(x).split()[0] for x in list(df.index)]
    df.index.rename("Date", inplace=True)
    df = df[-history:]

    return df.to_string()


# Script to scrap top5 googgle news for given company name
def google_query(search_term):
    if "news" not in search_term:
        search_term = search_term + " stock news"
    url = f"https://www.google.com/search?q={search_term}&cr=countryUS"
    url = re.sub(r"\s", "+", url)
    return url


def get_recent_stock_news(company_name):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
    }
    g_query = google_query(company_name)
    res = requests.get(g_query, headers=headers).text
    soup = BeautifulSoup(res, "html.parser")
    news = []
    for n in soup.find_all("div", "n0jPhd ynAwRc tNxQIb nDgy9d"):
        news.append(n.text)
    for n in soup.find_all("div", "IJl0Z"):
        news.append(n.text)

    if len(news) > 6:
        news = news[:4]
    else:
        news = news
    news_string = ""
    for i, n in enumerate(news):
        news_string += f"{i}. {n}\n"
    top5_news = "Recent News:\n\n" + news_string

    return top5_news


# Fetch financial statements from Yahoo Finance
def get_financial_statements(ticker):
    company = yf.Ticker(ticker)
    balance_sheet = company.balance_sheet
    if balance_sheet.shape[1] >= 3:
        balance_sheet = balance_sheet.iloc[:, :3]  # Remove 4th years data
    balance_sheet = balance_sheet.dropna(how="any")
    balance_sheet = balance_sheet.to_string()
    return balance_sheet


# Openai function calling
function = [
    {
        "name": "get_company_Stock_ticker",
        "description": "This will get the indian NSE/BSE stock ticker of the company",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker_symbol": {
                    "type": "string",
                    "description": "This is the stock symbol of the company.",
                },
                "company_name": {
                    "type": "string",
                    "description": "This is the name of the company given in query",
                },
            },
            "required": ["company_name", "ticker_symbol"],
        },
    }
]


def get_stock_ticker(query):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": f"Given the user request, what is the comapany name and the company stock ticker ?: {query}?",
            }
        ],
        functions=function,
        function_call={"name": "get_company_Stock_ticker"},
    )
    message = response["choices"][0]["message"]
    arguments = json.loads(message["function_call"]["arguments"])
    company_name = arguments["company_name"]
    company_ticker = arguments["ticker_symbol"]
    return company_name, company_ticker


def analyze_stock(query):
    company_name, ticker = get_stock_ticker(query)
    print({"Query": query, "Company_name": company_name, "Ticker": ticker})
    stock_data = get_stock_price(ticker, history=10)
    stock_financials = get_financial_statements(ticker)
    stock_news = get_recent_stock_news(company_name)

    available_information = f"Stock Price: {stock_data}\n\nStock Financials: {stock_financials}\n\nStock News: {stock_news}"
    user_message = f" User question: {query} \
            You have the following information available about {company_name}, {available_information} \
            Write (5-8) pointwise investment analysis to answer user query, At the end conclude with proper explaination. \
            Try to Give positives and negatives  : \
            "
    template = ChatPromptTemplate.from_messages(
        [
            SystemMessage(
                content=(
                    "Give detail stock analysis, Use the available data and provide investment recommendation"
                    "The user is fully aware about the investment risk, dont include any kind of warning such as 'It is recommended to conduct further research and analysis or consult with a financial advisor before making an investment decision' in the answer "
                )
            ),
            HumanMessage(content=(user_message)),
        ]
    )
    messages = template.format_messages(
        name="junk",
        information="junk",
        question=query,
    )
    analysis = llm(messages)
    return analysis.content
