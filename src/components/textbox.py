import dash_bootstrap_components as dbc
from dash import html

from app import app


def render_textbox(text: str, box: str = "AI"):
    text = text.replace(f"ChatBot:", "").replace("Human:", "")

    # Add CSS classes based on the 'box' parameter
    if box == "human":
        thumbnail_human = html.Img(
            src=app.get_asset_url("human.png"),
            className="thumbnail thumbnail-human",
        )
        textbox_human = dbc.Card(text, className="textbox-common textbox-human")
        return html.Div([thumbnail_human, textbox_human])

    elif box == "AI":
        thumbnail = html.Img(
            src=app.get_asset_url("chatbot.png"),
            className="thumbnail thumbnail-ai",
        )
        textbox = dbc.Card(text, className="textbox-common textbox-ai")

        return html.Div([thumbnail, textbox])

    else:
        raise ValueError("Incorrect option for `box`.")
