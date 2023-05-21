from dash import dcc, html, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
from app import app
from service.account_transactions import get_report
import pandas as pd

from utils.functions import formatter_currency_with_cents


SEARCH_RESULT = html.Div(id="home_content")


def on_search():
    df_puts = get_report(instrument_type="PUT")
    df_calls = get_report(instrument_type="CALL")
    return dbc.Container(
        dbc.Row(
            [
                dbc.Col(show_chart(df_puts, title="PUTS")),
                dbc.Col(show_chart(df_calls, title="CALLS")),
            ]
        ),
    )


def show_chart(df, title):
    if not df.empty:
        total = df["TOTAL_PRICE"].sum()
        message = html.Div(
            dbc.Alert(children=f"Total {title}: {formatter_currency_with_cents(total)}"),
        )
        # Populate chart
        fig = px.bar(
            df,
            x="CLOSE_DATE",
            y="TOTAL_PRICE",
            color="TICKER",
            text="TOTAL_PRICE",
        )
        fig.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
            height=400,
            paper_bgcolor="rgb(248, 248, 255)",
            plot_bgcolor="rgb(248, 248, 255)",
            bargap=0.6,
        )
        content = dcc.Graph(figure=fig)
        return (
            message,
            content,
        )
    else:
        return html.Div(
            dbc.Alert(children="No records"),
        )


layout = on_search()
