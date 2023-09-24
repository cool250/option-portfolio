import dash_bootstrap_components as dbc
from dash import callback, dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from components.input import render_chat_input
from components.textbox import render_textbox
from utils.fetch_stock_info import analyze_stock

# define layout
chatbot_layout = html.Div(
    html.Div(id="display-conversation"),
    className="chat-overview",
)


layout = html.Div(
    [
        dcc.Store(id="store-conversation", data=""),
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
                                            chatbot_layout,
                                            html.Div(
                                                render_chat_input(),
                                                className="margin-chat",
                                            ),
                                            dbc.Spinner(
                                                html.Div(id="loading-component")
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


@callback(
    Output(component_id="display-conversation", component_property="children"),
    Input(component_id="store-conversation", component_property="data"),
)
def update_display(chat_history):
    if chat_history is None:
        raise PreventUpdate
    return [
        render_textbox(x, box="human") if i % 2 == 0 else render_textbox(x, box="AI")
        for i, x in enumerate(chat_history.split("<split>")[:-1])
    ]


@callback(
    Output(component_id="user-input", component_property="value"),
    Input(component_id="submit", component_property="n_clicks"),
    Input(component_id="user-input", component_property="n_submit"),
)
def clear_input(n_clicks, n_submit):
    return ""


@callback(
    Output(component_id="store-conversation", component_property="data"),
    Output(component_id="loading-component", component_property="children"),
    Input(component_id="submit", component_property="n_clicks"),
    Input(component_id="user-input", component_property="n_submit"),
    State(component_id="user-input", component_property="value"),
    State(component_id="store-conversation", component_property="data"),
)
def run_chatbot(n_clicks, n_submit, user_input, chat_history):
    print("In run_chatbot")
    if n_clicks == 0 and n_submit is None:
        return "", None

    if user_input is None or user_input == "":
        return chat_history, None

    chat_history += f"Human: {user_input}<split>ChatBot: "
    result_ai = analyze_stock(query=user_input)
    model_output = result_ai.strip()
    chat_history += f"{model_output}<split>"
    return chat_history, None
