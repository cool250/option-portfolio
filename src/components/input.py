import dash_bootstrap_components as dbc


def render_chat_input():
    chat_input = dbc.InputGroup(
        children=[
            dbc.Input(
                id="user-input",
                placeholder="Input your investment related query...",
                type="text",
            ),
            dbc.Button(id="submit", children=">", color="success"),
        ],
    )
    return chat_input
