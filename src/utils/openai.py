import json
import logging

import openai
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.prompts import ChatPromptTemplate, PromptTemplate
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


def prediction(context, query):
    """
    Generate investment analysis based on user query and available stock information.

    Args:
        query (str): The user query appended with other stock context

    Returns:
        str: Investment analysis and recommendation.
    """
    # initialize the models
    openai = OpenAI()
    template = """You're a financial advisor. Answer the question based on the context below.

    Context: {context}

    Question: {query}

    Answer: """

    prompt_template = PromptTemplate(
        input_variables=["context", "query"], template=template
    )
    prompt = prompt_template.format(context=context, query=query)
    analysis = openai(prompt)
    logging.info(f"Open AI response {analysis}")
    return analysis
