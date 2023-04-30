import dash_bootstrap_components as dbc
import dash_tabulator
from dash import html
from dash.dependencies import Input, Output

from app import app
from service.accountpositions import AccountPositions
from utils.functions import formatter_currency

layout = dbc.Container(
    [
        dbc.Row(html.H4(children="PUTS")),
        html.Hr(className="my-2"),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            (
                                dbc.Alert(
                                    id="put-total",
                                    is_open=False,
                                )
                            )
                        ),
                        dbc.Spinner(html.Div(id="puts_table")),
                    ]
                )
            ]
        ),
        html.P(),
        dbc.Row(html.H4(children="CALLS")),
        html.Hr(className="my-2"),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Spinner(html.Div(id="calls_table")),
                )
            ]
        ),
        html.P(),
        dbc.Row(html.H4(children="STOCKS")),
        html.Hr(className="my-2"),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            (
                                dbc.Alert(
                                    id="stock-detail",
                                    is_open=False,
                                )
                            )
                        ),
                        dbc.Spinner(html.Div(id="stocks_table")),
                    ]
                )
            ]
        ),
    ],
    fluid=True,
)


@app.callback(
    [
        Output("puts_table", "children"),
        Output("calls_table", "children"),
        Output("stocks_table", "children"),
        Output("put-total", "is_open"),
        Output("put-total", "children"),
        Output("stock-detail", "is_open"),
        Output("stock-detail", "children"),
    ],
    [
       [Input('url', 'pathname')],
    ],
)
def on_button_click(n):
    positions = AccountPositions()

    df_puts = positions.get_put_positions()
    df_calls = positions.get_call_positions()
    df_stocks = positions.get_stock_positions()
    cash_required = formatter_currency(df_puts["COST"].sum())
    stock_value = formatter_currency(
        (df_stocks["TICKER PRICE"] * df_stocks["QTY"]).sum()
    )
    stock_cost = formatter_currency(
        (df_stocks["AVG PRICE"] * df_stocks["QTY"]).sum()
    )

    calls_dt = (
        dash_tabulator.DashTabulator(
            id="call-table",
            columns=[{"id": i, "title": i, "field": i} for i in df_calls.columns],
            data=df_calls.to_dict("records"),
        ),
    )

    stocks_dt = (
        dash_tabulator.DashTabulator(
            id="put-table",
            columns=[{"id": i, "title": i, "field": i} for i in df_stocks.columns],
            data=df_stocks.to_dict("records"),
        ),
    )

    puts_dt = (
        dash_tabulator.DashTabulator(
            id="put-table",
            columns=[{"id": i, "title": i, "field": i} for i in df_puts.columns],
            data=df_puts.to_dict("records"),
        ),
    )

    return (
        puts_dt,
        calls_dt,
        stocks_dt,
        True,
        f" Put Exposure : {cash_required}",
        True,
        f" Stock Value : {stock_value}  Stock Cost : {stock_cost}",
    )

