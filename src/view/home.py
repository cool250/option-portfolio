import dash_bootstrap_components as dbc
import plotly.express as px
from dash import Input, Output, callback, dcc, html
from dash.exceptions import PreventUpdate

from service.account_positions import AccountPositions
from utils.functions import formatter_currency_with_cents

layout = html.Div(id="home_content")


@callback(
    Output("home_content", "children"),
    Input("url", "href"),
)
def on_page_load(href):
    if href is None:
        raise PreventUpdate
    else:
        try:
            account = AccountPositions()
            df_puts = account.get_put_positions()
            df_calls = account.get_call_positions()
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
        except Exception as e:
            return html.Div(
                dbc.Alert(id="message", children=f"{str(e)}", color="danger"),
            )


def show_payoff_chart(df, title):
    if not df.empty:
        total = df["PREMIUM"].sum()
        # Populate chart
        fig = px.bar(
            df,
            x="CLOSE_DATE",
            y="PREMIUM",
            color="TICKER",
            text="PREMIUM",
            title=f"{title}: {formatter_currency_with_cents(total)}",
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
        total = df["COST"].sum()
        # Populate chart
        fig = px.bar(
            df,
            x="CLOSE_DATE",
            y="COST",
            color="TICKER",
            text="COST",
            title=f"Capital for Puts: {formatter_currency_with_cents(total)}",
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
