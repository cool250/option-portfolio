import logging
import re

import requests
from bs4 import BeautifulSoup


def google_query(search_term):
    """
    Generate a Google search URL for stock news related to the given search term.

    Args:
        search_term (str): The search term to be used in the Google query.

    Returns:
        str: The Google search URL.
    """
    if "news" not in search_term:
        search_term += " stock news"

    url = f"https://www.google.com/search?q={search_term}&cr=countryUS"
    url = re.sub(r"\s", "+", url)

    return url


def get_stock_news(company_name):
    """
    Get the top 4 recent stock news articles related to a given company.

    Args:
        company_name (str): The name of the company for which you want to retrieve news.

    Returns:
        str: A formatted string containing the top 4 recent news articles.
    """
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

    if len(news) > 4:
        news = news[:4]

    news_string = ""
    for i, n in enumerate(news):
        news_string += f"{i + 1}. {n}\n"

    top4_news = "Recent News:\n\n" + news_string
    logging.debug(f" Top News  for {company_name} : {top4_news}")

    return top4_news
