import logging
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from app import app
from service.account_transactions import get_report

TOP_COLUMN = dbc.Form(
    [
        dbc.Row(
            [
                dbc.Col(
                    children=[
                        dbc.Label("From Date", size="sm"),
                        dbc.Col(
                            dcc.DatePickerSingle(
                                id="db_start-date-picker",
                                display_format="YYYY-MM-DD",
                                date="2023-01-01",
                            ),
                        ),
                    ]
                ),
                dbc.Col(
                    children=[
                        dbc.Label("To Date", size="sm"),
                        dbc.Col(
                            dcc.DatePickerSingle(
                                id="db_end-date-picker",
                                display_format="YYYY-MM-DD",
                                placeholder="Enter Date",
                            ),
                        ),
                    ]
                ),
                dbc.Col(
                    children=[
                        dbc.Label("Ticker", size="sm"),
                        dbc.Input(
                            type="text",
                            id="db_report-ticker",
                            placeholder="symbol",
                            size="sm",
                        ),
                    ],
                ),
                dbc.Col(
                    children=[
                        dbc.Label("Instrument Type", size="sm"),
                        dbc.Select(
                            id="db_instrument-type",
                            options=[
                                {"label": "CALL", "value": "CALL"},
                                {"label": "PUT", "value": "PUT"},
                            ],
                            value="PUT",
                            size="sm",
                        ),
                    ],
                ),
                dbc.Col(
                    children=[
                        dbc.Button(
                            "Search",
                            color="primary",
                            id="chart-btn",
                            className="mt-4",
                        ),
                    ]
                ),
            ],
        ),
    ],
    className="p-2 bg-light border",
)

SEARCH_RESULT = html.Div(id="dashboard_content")

layout = dbc.Container(
    [
        dbc.Row(TOP_COLUMN),
        html.P(),
        dbc.Row(SEARCH_RESULT),
    ],
    fluid=True,
)


@app.callback(
    Output("dashboard_content", "children"),
    [
        Input("chart-btn", "n_clicks"),
    ],
    [
        State("db_start-date-picker", "date"),
        State("db_end-date-picker", "date"),
        State("db_report-ticker", "value"),
        State("db_instrument-type", "value"),
    ],
)
def on_search(n, start_date, end_date, ticker, instrument_type):
    df = get_report(start_date, end_date, ticker, instrument_type)

    if not df.empty:
        fig = px.bar(
            df, x="CLOSE_DATE", y="TOTAL_PRICE", color="TICKER", text="TOTAL_PRICE"
        )

        total = df["TOTAL_PRICE"].sum()
        return [
            html.Div(
                dbc.Alert(id="total-message", children=f"Total : {total}"),
            ),
            dcc.Graph(id="graph", figure=fig),
        ]
    else:
        return html.Div(
            dbc.Alert(id="total-message", children="No records"),
        )
