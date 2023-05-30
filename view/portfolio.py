import dash_bootstrap_components as dbc
import dash_tabulator
from dash import html, dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app
from opstrat.basic_multi import multi_plotter
from service.account_positions import AccountPositions
from utils.functions import formatter_currency

layout = dbc.Container(
    dbc.Spinner(
        [
            dbc.Row(
                dbc.Modal(
                    [
                        dbc.ModalHeader("Payoff"),
                        dbc.ModalBody(
                            id="payoff-chart",
                        ),
                    ],
                    id="payoff-modal",
                    centered=True,
                    size="xl",
                ),
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Button(
                            "Calculate Payoff",
                            color="primary",
                            id="payoff-btn",
                            className="mt-4",
                        ),
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

    puts_dt = (
        dash_tabulator.DashTabulator(
            id="put-table",
            data=df_puts.to_dict("records"),
            options=tabulator_options,
            columns = [
                {"title": "QTY", "field": "QTY"},
                {"title": "UNDERLYING", "field": "TICKER", "headerFilter": "input"},
                {"title": "SYMBOL", "field": "SYMBOL"},
                {"title": "UNDERLYING PRICE", "field": "TICKER PRICE"},
                {"title": "STRIKE", "field": "STRIKE PRICE"},
                {"title": "MARK", "field": "MARK"},
                {"title": "PURCHASE", "field": "PURCHASE PRICE"},
                {"title": "DAYS", "field": "DAYS"},
                {"title": "ITM", "field": "ITM"},
                {"title": "DELTA", "field": "DELTA"},
                {"title": "RETURNS", "field": "RETURNS"},
                {"title": "MARGIN", "field": "MARGIN", "visible":False},
                {"title": "THETA", "field": "THETA", "visible":False },
                {"title": "COST", "field": "COST", "visible":False},
                
            ]
        ),
    )
    calls_dt = (
        dash_tabulator.DashTabulator(
            id="call-table",
            data=df_calls.to_dict("records"),
            options=tabulator_options,
            columns = [
                {"title": "QTY", "field": "QTY"},
                {"title": "UNDERLYING", "field": "TICKER", "headerFilter": "input"},
                {"title": "SYMBOL", "field": "SYMBOL"},
                {"title": "UNDERLYING PRICE", "field": "TICKER PRICE"},
                {"title": "STRIKE", "field": "STRIKE PRICE"},
                {"title": "MARK", "field": "MARK"},
                {"title": "PURCHASE", "field": "PURCHASE PRICE"},
                {"title": "DAYS", "field": "DAYS"},
                {"title": "ITM", "field": "ITM"},
                {"title": "DELTA", "field": "DELTA"},
                {"title": "MARGIN", "field": "MARGIN", "visible":False},
                {"title": "THETA", "field": "THETA", "visible":False},
            ]
        ),
    )
    stocks_dt = (
        dash_tabulator.DashTabulator(
            id="stock-table",
            data=df_stocks.to_dict("records"),
            options=tabulator_options,
            columns = [
                {"title": "QTY", "field": "QTY"},
                {"title": "TICKER", "field": "TICKER", "headerFilter": "input"},
                {"title": "MARK", "field": "MARK"},
                {"title": "AVG COST", "field": "AVG COST"},
                {"title": "MARGIN", "field": "MARGIN"},
                {"title": "NET", "field": "NET"},
            ]
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
    [
    Output("payoff-chart", "children"),
    Output("payoff-modal", "is_open"),
    ],
    Input("payoff-btn", "n_clicks"),
    [State("put-table", "multiRowsClicked"), State("call-table", "multiRowsClicked")],
    prevent_initial_call=True,
)
def display_output(n, put_trades, call_trades):
    spot_price = 0
    trades = []
    if n is None or (len(call_trades) == 0 and len(put_trades) == 0):
        raise PreventUpdate
    else:
        for put_trade in put_trades:
            trade_dict = {}
            if spot_price == 0:  # populate jsut once
                spot_price = put_trade["TICKER PRICE"]
            trade_dict["op_type"] = "p"
            trade_dict["op_pr"] = put_trade["PURCHASE PRICE"]
            trade_dict["strike"] = put_trade["STRIKE PRICE"]
            if put_trade["QTY"] < 0:
                trade_dict["contract"] = -put_trade["QTY"]
                trade_dict["tr_type"] = "s"
            else:
                trade_dict["contract"] = put_trade["QTY"]
                trade_dict["tr_type"] = "b"

            trades.append(trade_dict)

        for call_trade in call_trades:
            trade_dict = {}
            if spot_price == 0:  # populate jsut once
                spot_price = call_trade["TICKER PRICE"]
            trade_dict["op_type"] = "c"
            trade_dict["op_pr"] = call_trade["PURCHASE PRICE"]
            trade_dict["strike"] = call_trade["STRIKE PRICE"]
            if call_trade["QTY"] < 0:
                trade_dict["contract"] = -call_trade["QTY"]
                trade_dict["tr_type"] = "s"
            else:
                trade_dict["contract"] = call_trade["QTY"]
                trade_dict["tr_type"] = "b"
            trades.append(trade_dict)

        # Plot the trades
        spot_price = float(spot_price)
        fig = multi_plotter(spot=spot_price, op_list=trades)
        chart = html.Div(
            [
                dcc.Graph(figure=fig),
            ]
        )
        return chart, True