import dash_bootstrap_components as dbc
from dash import callback, dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from components.input import render_chat_input
from components.textbox import render_textbox
from utils.fetch_stock_info import analyze_stock

# Define the layout for the chatbot application
chatbot_layout = html.Div(
    html.Div(id="display-conversation"),
    className="chat-overview",
)

# Create the main layout of the application
layout = html.Div(
    [
        dcc.Store(id="store-conversation", data=""),  # Store for chat history
        dbc.Container(
            fluid=True,
            children=[
                dbc.Row(
                    [
                        dbc.Col(width=1),
                        dbc.Col(
                            width=10,
                            children=dbc.Card(
                                [
                                    dbc.CardBody(
                                        [
                                            chatbot_layout,  # Display chat history
                                            html.Div(
                                                render_chat_input(),  # Render user input field
                                                className="margin-chat",
                                            ),
                                            dbc.Spinner(
                                                html.Div(
                                                    id="loading-component"
                                                )  # Loading spinner
                                            ),
                                        ]
                                    )
                                ],
                                className="border-radius-25",
                            ),
                        ),
                        dbc.Col(width=1),
                    ]
                )
            ],
        ),
    ],
)


# Callback to update the displayed conversation
@callback(
    Output(component_id="display-conversation", component_property="children"),
    Input(component_id="store-conversation", component_property="data"),
)
def update_display(chat_history):
    """
    Updates the displayed conversation based on the chat history.

    Args:
        chat_history (str): The chat history as a single string.

    Returns:
        list: A list of rendered textboxes representing the conversation.
    """
    if chat_history is None:
        raise PreventUpdate
    return [
        render_textbox(x, box="human") if i % 2 == 0 else render_textbox(x, box="AI")
        for i, x in enumerate(chat_history.split("<split>")[:-1])
    ]


# Callback to clear user input field
@callback(
    Output(component_id="user-input", component_property="value"),
    Input(component_id="submit", component_property="n_clicks"),
    Input(component_id="user-input", component_property="n_submit"),
)
def clear_input(n_clicks, n_submit):
    """
    Clears the user input field after submission.

    Args:
        n_clicks (int): The number of times the submit button is clicked.
        n_submit (int): The number of times the user presses Enter in the input field.

    Returns:
        str: An empty string to clear the user input field.
    """
    return ""


# Callback to run the chatbot and update the chat history
@callback(
    Output(component_id="store-conversation", component_property="data"),
    Output(component_id="loading-component", component_property="children"),
    Input(component_id="submit", component_property="n_clicks"),
    Input(component_id="user-input", component_property="n_submit"),
    State(component_id="user-input", component_property="value"),
    State(component_id="store-conversation", component_property="data"),
)
def run_chatbot(n_clicks, n_submit, user_input, chat_history):
    """
    Runs the chatbot logic and updates the chat history.

    Args:
        n_clicks (int): The number of times the submit button is clicked.
        n_submit (int): The number of times the user presses Enter in the input field.
        user_input (str): The user's input text.
        chat_history (str): The current chat history.

    Returns:
        tuple: A tuple containing the updated chat history and None for the loading component.
    """
    if n_clicks == 0 and n_submit is None:
        return "", None

    if user_input is None or user_input == "":
        return chat_history, None

    chat_history += f"Human: {user_input}<split>ChatBot: "
    result_ai = analyze_stock(user_query=user_input)
    model_output = result_ai.strip()
    chat_history += f"{model_output}<split>"
    return chat_history, None
