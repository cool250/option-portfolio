import json

import openai
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.prompts.chat import HumanMessage, SystemMessage

function = [
    {
        "name": "get_company_Stock_ticker",
        "description": "This function retrieves the stock ticker of a company.",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker_symbol": {
                    "type": "string",
                    "description": "The stock symbol of the company.",
                },
                "company_name": {
                    "type": "string",
                    "description": "The name of the company given in the query.",
                },
            },
            "required": ["company_name", "ticker_symbol"],
        },
    }
]


def get_stock_ticker(query):
    """
    Retrieve the stock ticker symbol of a company based on a user query.

    Args:
        query (str): The user query to extract the company name and stock ticker.

    Returns:
        tuple: A tuple containing the company name and stock ticker symbol.
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": f"Given the user request, what is the company name and the company stock ticker?: {query}",
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


def prediction(query):
    """
    Generate investment analysis based on user query and available stock information.

    Args:
        query (str): The user query appended with other stock context

    Returns:
        str: Investment analysis and recommendation.
    """
    chat = ChatOpenAI()
    template = ChatPromptTemplate.from_messages(
        [
            SystemMessage(
                content=(
                    "Give detailed stock analysis. Use the available data to provide investment recommendations."
                    "The user is fully aware of the investment risk. Do not explicitly include any kind of warning such as 'It is recommended to conduct further research and analysis or consult with a financial advisor before making an investment decision' in the answer."
                )
            ),
            HumanMessage(content=(query)),
        ]
    )
    messages = template.format_messages()
    analysis = chat(messages)
    return analysis.content
