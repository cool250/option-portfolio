from dash import dcc, html, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
from app import app
from service.account_transactions import get_report
import pandas as pd

from utils.functions import formatter_currency_with_cents


SEARCH_RESULT = html.Div(id="home_content")


def on_page_load():
    df_puts = get_report(instrument_type="PUT")
    df_calls = get_report(instrument_type="CALL")
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(show_payoff_chart(df_puts, title="PUTS")),
                    dbc.Col(show_payoff_chart(df_calls, title="CALLS")),
                ]
            ),
            html.P(),
            dbc.Row(show_capital_need(df_puts)),
        ]
    )


def show_payoff_chart(df, title):
    if not df.empty:
        total = df["TOTAL_PRICE"].sum()
        # Populate chart
        fig = px.bar(
            df,
            x="CLOSE_DATE",
            y="TOTAL_PRICE",
            color="TICKER",
            text="TOTAL_PRICE",
            title=f"Total {title}: {formatter_currency_with_cents(total)}",
        )
        fig.update_layout(
            bargap=0.6,
        )
        content = dcc.Graph(figure=fig)
        return content
    else:
        return html.Div(
            dbc.Alert(children="No records"),
        )


def show_capital_need(df):
    if not df.empty:
        df["TOTAL_COST"] = df["STRIKE_PRICE"].astype(float) * df["QTY"] * 100
        total = df["TOTAL_COST"].sum()
        # Populate chart
        fig = px.bar(
            df,
            x="CLOSE_DATE",
            y="TOTAL_COST",
            color="TICKER",
            text="TOTAL_COST",
            title=f"Total Capital for Puts: {formatter_currency_with_cents(total)}",
        )
        fig.update_layout(
            bargap=0.6,
        )
        content = dcc.Graph(figure=fig)
        return content
    else:
        return html.Div(
            dbc.Alert(children="No records"),
        )
layout = on_page_load()
