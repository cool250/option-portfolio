import logging
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from app import app
from service.account_transactions import get_report

TOP_COLUMN = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            dbc.Label(
                                "From Date",
                            ),
                            dbc.Col(
                                dcc.DatePickerSingle(
                                    id="db_start-date-picker",
                                    display_format="YYYY-MM-DD",
                                    date="2023-01-01",
                                ),
                            ),
                        ]
                    ),
                ),
                dbc.Col(
                    html.Div(
                        [
                            dbc.Label(
                                "To Date",
                            ),
                            dbc.Col(
                                dcc.DatePickerSingle(
                                    id="db_end-date-picker",
                                    display_format="YYYY-MM-DD",
                                    placeholder="Enter Date",
                                ),
                            ),
                        ]
                    ),
                ),
                dbc.Col(
                    html.Div(
                        [
                            dbc.Label("Ticker", html_for="example-email-grid"),
                            dbc.Input(
                                type="text",
                                id="db_report-ticker",
                                placeholder="symbol",
                            ),
                        ],
                    ),
                ),
                dbc.Col(
                    html.Div(
                        [
                            dbc.Label("Instrument Type", html_for="example-email-grid"),
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
                ),
            ],
        ),
        html.Div(
            dbc.Button(
                "Search",
                color="primary",
                id="chart-btn",
            ),
            className="d-md-flex justify-content-md-end mt-3",
        ),
    ],
    className="p-3 bg-light border",
)

SEARCH_RESULT = html.Div(
    [
        html.Div(
            dbc.Alert(
                id="total-message",
                color="primary",
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
        fig = px.bar(df, x="CLOSE_DATE", y = "TOTAL_PRICE", color="TICKER")

        # Add Trace for displaying total sum on top of stacked bar chart
        
        # Sum the totals for a given close date
        dfs = df.groupby('CLOSE_DATE').sum() 

        total = df['TOTAL_PRICE'].sum()

        # Create a scatter trace
        fig.add_trace(go.Scatter(
            x=dfs.index, 
            y=dfs['TOTAL_PRICE'],
            text=dfs['TOTAL_PRICE'],
            mode='text',
            textposition='top center',
            textfont=dict(
                size=10,
            ),
            showlegend=False
        ))
        return total, fig
    else:
        return "No records", {}

