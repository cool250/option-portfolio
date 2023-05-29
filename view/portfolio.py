import dash_bootstrap_components as dbc
import dash_tabulator
from dash import html, dcc
from dash.dependencies import Input, Output, State

from app import app
from opstrat.basic_multi import multi_plotter
from service.account_positions import AccountPositions
from utils.functions import formatter_currency

layout = dbc.Container(
    dbc.Spinner(
        [
            dbc.Row(
                [
                    dbc.Col(
                        children=[
                            dbc.Button(
                                "Payoff",
                                color="primary",
                                id="payoff-btn",
                                className="mt-4",
                            ),
                        ],
                    ),
                ],
            ),
            html.P(),
            dbc.Row(html.H4(children="PUTS")),
            html.Hr(className="my-2"),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(id="dummy-output"),
                            html.Div(id="put-detail"),
                            html.P(),
                            html.Div(id="puts_table"),
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
                        html.Div(id="calls_table"),
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
                            html.Div(id="stock-detail"),
                            html.P(),
                            html.Div(id="stocks_table"),
                        ]
                    )
                ]
            ),
        ],
    ),
)


@app.callback(
    [
        Output("puts_table", "children"),
        Output("calls_table", "children"),
        Output("stocks_table", "children"),
        Output("put-detail", "children"),
        Output("stock-detail", "children"),
    ],
    [
        [Input("url", "pathname")],
    ],
)
def on_button_click(n):
    positions = AccountPositions()

    df_puts = positions.get_put_positions()
    df_calls = positions.get_call_positions()
    df_stocks = positions.get_stock_positions()
    cash_required = formatter_currency(df_puts["COST"].sum())
    puts_maintenance = formatter_currency(df_puts["MARGIN"].sum())
    stock_value = formatter_currency(
        (df_stocks["CURRENT PRICE"] * df_stocks["QTY"]).sum()
    )
    stock_cost = formatter_currency((df_stocks["AVG COST"] * df_stocks["QTY"]).sum())
    stocks_maintenance = formatter_currency(df_stocks["MARGIN"].sum())

    tabulator_options = {
        "selectable": "true",
    }
    calls_dt = (
        dash_tabulator.DashTabulator(
            id="call-table",
            columns=[{"id": i, "title": i, "field": i} for i in df_calls.columns],
            data=df_calls.to_dict("records"),
            options=tabulator_options,
        ),
    )

    stocks_dt = (
        dash_tabulator.DashTabulator(
            id="stocks-table",
            columns=[{"id": i, "title": i, "field": i} for i in df_stocks.columns],
            data=df_stocks.to_dict("records"),
            options=tabulator_options,
        ),
    )
  

    puts_dt = (
        dash_tabulator.DashTabulator(
            id="put-table",
            columns=[{"id": i, "title": i, "field": i} for i in df_puts.columns],
            data=df_puts.to_dict("records"),
            options=tabulator_options,
        ),
    )

    return (
        puts_dt,
        calls_dt,
        stocks_dt,
        html.Div(
            [
                f" Put Exposure : {cash_required} Maintenance: {puts_maintenance}",
                html.Br(),
            ]
        ),
        html.Div(
            [
                f" Stock Value : {stock_value}  Stock Cost : {stock_cost}  Maintenance: {stocks_maintenance}",
                html.Br(),
            ]
        ),
    )

# dash_tabulator can register a callback on rowClicked
# to receive a dict of the row values
@app.callback(
    Output("dummy-output", "children"),
    Input("payoff-btn", "n_clicks"),
    State("put-table", "multiRowsClicked"),
)
def display_output(n, put_trades):
    spot_price = 0
    trades = []
    if n is None or put_trades is None or len(put_trades) == 0:
        return 0
    else:
        for put_trade in put_trades:
            trade_dict = {}
            if spot_price == 0: # populate jsut once
                spot_price = put_trade['TICKER PRICE']
            trade_dict['op_type'] = 'p'
            trade_dict['op_pr'] = put_trade['PURCHASE PRICE']
            if put_trade['QTY']  < 0:
                trade_dict['contract'] = -put_trade['QTY'] 
                trade_dict['tr_type'] = 's'
            else:
                trade_dict['contract'] = put_trade['QTY'] 
                trade_dict['tr_type'] = 'b'
            trade_dict['strike'] = put_trade['STRIKE PRICE']
            trades.append(trade_dict)
            
        spot_price = float(spot_price)
        fig = multi_plotter(spot=spot_price, op_list=trades)
        return dcc.Graph(figure=fig)




