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
                        [
                            dbc.Row(html.H4(children="BALANCE")),
                            html.Hr(className="my-2"),
                            dbc.Row(
                                html.Div(id="balance-detail"),
                            ),
                        ],
                        width=10
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Calculate Payoff",
                            color="primary",
                            id="payoff-btn",
                            className="mt-4",
                        ),
                        class_name="text-end",
                    ),
                ],
            ),
            html.P(),
            dbc.Row(html.H4(children="PUTS")),
            html.Hr(className="my-2"),
            dbc.Row(
                [
                    html.Div(id="dummy-output"),
                    html.Div(id="put-detail"),
                    html.P(),
                    html.Div(id="puts_table"),
                ]
            ),
            html.P(),
            dbc.Row(html.H4(children="CALLS")),
            html.Hr(className="my-2"),
            dbc.Row(
                html.Div(id="calls_table"),
            ),
            html.P(),
            dbc.Row(html.H4(children="STOCKS")),
            html.Hr(className="my-2"),
            dbc.Row(
                [
                    html.Div(id="stock-detail"),
                    html.P(),
                    html.Div(id="stocks_table"),
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
        Output("balance-detail", "children"),
        Output("put-detail", "children"),
        Output("stock-detail", "children"),
    ],
    [
        [Input("url", "pathname")],
    ],
)
def on_button_click(n):
    account = AccountPositions()
    balance = account.get_account(field="balances")
    df_puts = account.get_put_positions()
    df_calls = account.get_call_positions()
    df_stocks = account.get_stock_positions()
    puts_cash = formatter_currency(df_puts["COST"].sum())
    puts_maintenance = formatter_currency(df_puts["MARGIN"].sum())
    stock_value = formatter_currency((df_stocks["MARK"] * df_stocks["QTY"]).sum())
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
            columns=[
                {"title": "QTY", "field": "QTY"},
                {"title": "UNDERLYING", "field": "TICKER", "headerFilter": "input"},
                {"title": "SYMBOL", "field": "SYMBOL"},
                {"title": "UNDERLYING PRICE", "field": "UNDERLYING PRICE"},
                {"title": "STRIKE", "field": "STRIKE PRICE"},
                {"title": "MARK", "field": "MARK"},
                {"title": "PURCHASE", "field": "PURCHASE PRICE"},
                {"title": "DAYS", "field": "DAYS"},
                {"title": "ITM", "field": "ITM"},
                {"title": "DELTA", "field": "DELTA"},
                {"title": "RETURNS", "field": "RETURNS"},
                {"title": "MARGIN", "field": "MARGIN", "visible": False},
                {"title": "THETA", "field": "THETA"},
                {"title": "COST", "field": "COST", "visible": False},
            ],
        ),
    )
    calls_dt = (
        dash_tabulator.DashTabulator(
            id="call-table",
            data=df_calls.to_dict("records"),
            options=tabulator_options,
            columns=[
                {"title": "QTY", "field": "QTY"},
                {"title": "UNDERLYING", "field": "TICKER", "headerFilter": "input"},
                {"title": "SYMBOL", "field": "SYMBOL"},
                {"title": "UNDERLYING PRICE", "field": "UNDERLYING PRICE"},
                {"title": "STRIKE", "field": "STRIKE PRICE"},
                {"title": "MARK", "field": "MARK"},
                {"title": "PURCHASE", "field": "PURCHASE PRICE"},
                {"title": "DAYS", "field": "DAYS"},
                {"title": "ITM", "field": "ITM"},
                {"title": "DELTA", "field": "DELTA"},
                {"title": "MARGIN", "field": "MARGIN", "visible": False},
                {"title": "THETA", "field": "THETA", "visible": False},
            ],
        ),
    )
    stocks_dt = (
        dash_tabulator.DashTabulator(
            id="stock-table",
            data=df_stocks.to_dict("records"),
            options=tabulator_options,
            columns=[
                {"title": "QTY", "field": "QTY"},
                {"title": "TICKER", "field": "TICKER", "headerFilter": "input"},
                {"title": "MARK", "field": "MARK"},
                {"title": "AVG COST", "field": "AVG COST"},
                {"title": "MARGIN", "field": "MARGIN"},
                {"title": "NET", "field": "NET"},
            ],
        ),
    )

    return (
        puts_dt,
        calls_dt,
        stocks_dt,
        html.Div(
            [
                f" Account Value : {formatter_currency(balance.accountValue)} Cash Balance : {formatter_currency(balance.marginBalance)} Maintenance Requirements: {formatter_currency(balance.maintenanceRequirement)}",
                html.Br(),
            ]
        ),
        html.Div(
            [
                f" Put Exposure : {puts_cash} Maintenance: {puts_maintenance}",
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
    [
        State("put-table", "multiRowsClicked"),
        State("call-table", "multiRowsClicked"),
        State("stock-table", "multiRowsClicked"),
    ],
    prevent_initial_call=True,
)
def display_output(n, put_trades, call_trades, stock_trades):
    spot_price = 0
    trades = []

    def populate_selected_trades(trade, op_type):
        nonlocal spot_price
        nonlocal trades
        if spot_price == 0:  # populate just once for underlying
            spot_price = trade["UNDERLYING PRICE"]

        trade_dict = {}
        trade_dict["op_type"] = op_type
        trade_dict["op_pr"] = trade["PURCHASE PRICE"]
        trade_dict["strike"] = trade["STRIKE PRICE"]
        if trade["QTY"] < 0:  # Sell
            trade_dict["contract"] = -trade["QTY"]
            trade_dict["tr_type"] = "s"
        else:  # Buy
            trade_dict["contract"] = trade["QTY"]
            trade_dict["tr_type"] = "b"
        trades.append(trade_dict)

    if n is None or (len(call_trades) == 0 and len(put_trades) == 0):
        raise PreventUpdate

    else:
        for trade in put_trades:
            populate_selected_trades(trade, op_type="p")

        for trade in call_trades:
            populate_selected_trades(trade, op_type="c")

        for trade in stock_trades:
            trade_dict = {}
            trade_dict["op_type"] = "e"
            trade_dict["op_pr"] = 0
            trade_dict["strike"] = trade["AVG COST"]
            trade_dict["contract"] = trade["QTY"] / 100
            trade_dict["tr_type"] = "b"
            trades.append(trade_dict)

        # Plot the trades
        fig = multi_plotter(spot=spot_price, op_list=trades)
        chart = html.Div(
            [
                dcc.Graph(figure=fig),
            ]
        )
        return chart, True
