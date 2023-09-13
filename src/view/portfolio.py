import dash_bootstrap_components as dbc
import dash_tabulator
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app
from service.account_positions import AccountPositions
from utils.functions import formatter_currency
from utils.opstrat.basic_multi import multi_plotter

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
                        width=10,
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
                    html.Div(id="puts_table"),
                ]
            ),
            html.P(),
            dbc.Row(html.H4(children="CALLS")),
            html.Hr(className="my-2"),
            dbc.Row(
                [
                    html.Div(id="call-detail"),
                    html.Div(id="calls_table"),
                ]
            ),
            html.P(),
            dbc.Row(html.H4(children="STOCKS")),
            html.Hr(className="my-2"),
            dbc.Row(
                [
                    html.Div(id="stock-detail"),
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
        Output("call-detail", "children"),
        Output("stock-detail", "children"),
    ],
    [
        [Input("url", "pathname")],
    ],
)
def on_button_click(n):
    """Display account summary and positions tables.

    Retrieves account balance, put positions, call positions, and stock positions.
    Renders the data in Tabulator tables and summary alerts.

    Returns:
        puts_table (DashTabulator): Put positions table
        calls_table (DashTabulator): Call positions table
        stocks_table (DashTabulator): Stock positions table
        balance_detail (html.Div): Account balance summary alert
        put_detail (html.Div): Put positions summary alert
        call_detail (html.Div): Call positions summary alert
        stock_detail (html.Div): Stock positions summary alert
    """
    account = AccountPositions()
    balance = account.balance
    df_puts = account.get_put_positions()
    df_calls = account.get_call_positions()
    df_stocks = account.get_stock_positions()
    puts_count = df_puts.shape[0]
    calls_count = df_calls.shape[0]
    stocks_count = df_stocks.shape[0]
    puts_cash = formatter_currency(df_puts["COST"].sum())
    puts_maintenance = formatter_currency(df_puts["MARGIN"].sum())
    calls_maintenance = formatter_currency(df_calls["MARGIN"].sum())
    stock_value = (df_stocks["MARK"] * df_stocks["QTY"]).sum()
    format_stock_value = formatter_currency(stock_value)
    stock_cost = (df_stocks["AVG COST"] * df_stocks["QTY"]).sum()
    format_stock_cost = formatter_currency(stock_cost)
    stock_profit = formatter_currency(stock_value - stock_cost)
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
                {"title": "UNDERLYING", "field": "TICKER", "headerFilter": "input"},
                {"title": "QTY", "field": "QTY"},
                {"title": "SYMBOL", "field": "SYMBOL"},
                {"title": "PREMIUM", "field": "PREMIUM"},
                {"title": "UNDERLYING PRICE", "field": "UNDERLYING PRICE"},
                {"title": "STRIKE", "field": "STRIKE PRICE"},
                {"title": "MARK", "field": "MARK"},
                {"title": "PURCHASE", "field": "PURCHASE PRICE"},
                {"title": "DAYS", "field": "DAYS"},
                {"title": "ITM", "field": "ITM"},
                {"title": "RETURNS", "field": "RETURNS"},
                {"title": "MARGIN", "field": "MARGIN", "visible": False},
                {"title": "THETA", "field": "THETA"},
                {"title": "DELTA", "field": "DELTA"},
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
                {"title": "UNDERLYING", "field": "TICKER", "headerFilter": "input"},
                {"title": "QTY", "field": "QTY"},
                {"title": "SYMBOL", "field": "SYMBOL"},
                {"title": "UNDERLYING PRICE", "field": "UNDERLYING PRICE"},
                {"title": "STRIKE", "field": "STRIKE PRICE"},
                {"title": "EXTRINSIC", "field": "EXTRINSIC"},
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
                {"title": "TICKER", "field": "TICKER", "headerFilter": "input"},
                {"title": "QTY", "field": "QTY"},
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
                dbc.Alert(
                    children=f" Account Value:{formatter_currency(balance.accountValue)}  Cash Balance:{formatter_currency(balance.marginBalance)}  Maintenance:{formatter_currency(balance.maintenanceRequirement)}",
                    color="info",
                ),
            ]
        ),
        html.Div(
            [
                dbc.Alert(
                    children=f"Total:{puts_count}  Exposure:{puts_cash} Maintenance:{puts_maintenance}",
                    color="info",
                ),
            ]
        ),
        html.Div(
            [
                dbc.Alert(
                    children=f"Total:{calls_count} Maintenance:{calls_maintenance}",
                    color="info",
                ),
            ]
        ),
        html.Div(
            [
                dbc.Alert(
                    children=f"Total:{stocks_count}  Value:{format_stock_value}   Cost:{format_stock_cost}  P/L: {stock_profit} Maintenance:{stocks_maintenance}",
                    color="info",
                ),
            ]
        ),
    )


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
    """Plot payoff diagram for selected positions.

    When payoff button is clicked, renders a payoff diagram based on currently
    selected rows in the positions tables.

    Args:
        n (int): Payoff button click
        put_trades (list): Selected put position rows
        call_trades (list): Selected call position rows
        stock_trades (list): Selected stock position rows

    Returns:
        chart (html.Div): Plotly graph with payoff diagram
        is_open (bool): Whether to open the modal
    """
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
            trade_dict["contract"] = int(trade["QTY"] / 100)
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
