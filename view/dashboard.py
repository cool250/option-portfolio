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
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            dbc.Button(
                "Search",
                color="primary",
                id="chart-btn",
                outline=True,
                type="submit",
                size="sm",
            ),
            className="d-md-flex justify-content-md-end mt-3",
        ),
    ],
    className="p-2 bg-light border",
)

SEARCH_RESULT = html.Div(
    [
        html.Div(
            dbc.Alert(
                id="total-message",
            ),
        ),
        dcc.Graph(id="graph"),
    ]
)

layout = dbc.Container(
    [
        dbc.Row(TOP_COLUMN),
        html.P(),
        dbc.Row(SEARCH_RESULT),
    ],
    fluid=True,
)


@app.callback(
    Output("total-message", "children"),
    Output("graph", "figure"),
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

        # Add Trace for displaying total sum on top of stacked bar chart

        # Sum the totals for a given close date
        dfs = df.groupby("CLOSE_DATE").sum()

        total = df["TOTAL_PRICE"].sum()

        return f"Total : {total}", fig
    else:
        return "No records", {}
