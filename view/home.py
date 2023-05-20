from dash import dcc, html, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
from app import app
from service.account_transactions import get_report
import pandas as pd


SEARCH_RESULT = html.Div(id="home_content")

def on_search():
    df_puts = get_report(instrument_type="PUT")
    df_calls = get_report(instrument_type="CALL")
    return dbc.Container(
    [
        dbc.Row(html.H4(children="PUTS")),
        dbc.Row(show_chart(df_puts)),
        html.P(),
        dbc.Row(html.H4(children="CALLS")),
        dbc.Row(show_chart(df_calls)),
    ],
    fluid=True,
)

def show_chart(df):
    if not df.empty:
        total = df["TOTAL_PRICE"].sum()
        message = html.Div(
            dbc.Alert(children=f"Total : {total}"),
        )
        # Populate chart
        fig = px.bar(
            df, x="CLOSE_DATE", y="TOTAL_PRICE", color="TICKER", text="TOTAL_PRICE",
        )
        fig.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
            width=800,
            height=400,
            paper_bgcolor="LightSteelBlue",
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