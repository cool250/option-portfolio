from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import dash_tabulator
import plotly.express as px
from app import app
from service.account_transactions import get_report
from utils.functions import change_date_format, formatter_currency_with_cents

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
                                {"label": "ALL", "value": "ALL"},
                            ],
                            value="ALL",
                            size="sm",
                        ),
                    ],
                ),
                dbc.Col(
                    children=[
                        dbc.Label("Report Type", size="sm"),
                        dbc.Select(
                            id="db_report-type",
                            options=[
                                {"label": "TABLE", "value": "TABLE"},
                                {"label": "CHART", "value": "CHART"},
                            ],
                            value="TABLE",
                            size="sm",
                        ),
                    ]
                ),
                dbc.Col(
                    children=[
                        dbc.Button(
                            "Search",
                            color="primary",
                            id="chart-btn",
                            className="mt-4",
                            size="md"
                        ),
                    ],
                    className="text-end",
                ),
            ],
        ),
    ],
    className="p-2",
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
        State("db_report-ticker", "value"),
        State("db_instrument-type", "value"),
        State("db_report-type", "value"),
        State("db_start-date-picker", "date"),
        State("db_end-date-picker", "date"),
    ],
)
def on_search(n, ticker, instrument_type, report_type, start_date, end_date):
    df = get_report(start_date, end_date, ticker, instrument_type)

    if not df.empty:
        total = df["TOTAL_PRICE"].sum()
        message = html.Div(
            dbc.Alert(id="total-message", children=f"{formatter_currency_with_cents(total)}", color="info"),
        )
        # Populate data table
        if report_type == "TABLE":
            # Change open and close date format to mm/dd/yy to match TD reports for reconcile later
            df["DATE"] = df["DATE"].apply(change_date_format)
            df["CLOSE_DATE"] = df["CLOSE_DATE"].apply(change_date_format)
            columns = [
                {"title": "TICKER", "field": "TICKER", "headerFilter": "input"},
                {"title": "TYPE", "field": "INSTRUCTION"},
                {"title": "OPEN DATE", "field": "DATE"},
                {"title": "CLOSE DATE", "field": "CLOSE_DATE"},
                {"title": "STRIKE_PRICE", "field": "STRIKE_PRICE"},
                {
                    "title": "TOTAL PRICE",
                    "field": "TOTAL_PRICE",
                    "topCalc": "sum",
                    "topCalcParams": {
                        "precision": 2,
                    },
                },
                {"title": "OPEN PRICE", "field": "PRICE"},
                {"title": "CLOSE PRICE", "field": "CLOSE_PRICE"},
                {"title": "QTY", "field": "QTY"},
                {"title": "SYMBOL", "field": "SYMBOL"},
                {
                    "title": "STATUS",
                    "field": "STATUS",
                    "headerFilter": "input",
                    "topCalc": "count",
                },
            ]
            dt = (
                dash_tabulator.DashTabulator(
                    id="report-table",
                    columns=columns,
                    data=df.to_dict("records"),
                    # Disable for now - do not remove code
                    # downloadButtonType={
                    #     "css": "btn btn-primary mb-3",
                    #     "text": "Export",
                    #     "type": "csv",
                    # },
                ),
            )
            content = html.Div(children=dt)
        else:
            # Populate chart
            fig = px.bar(
                df, x="CLOSE_DATE", y="TOTAL_PRICE", color="TICKER", text="TOTAL_PRICE"  
            )
            fig.update_layout(           
                height=400,
                bargap=0.1,
            )
            content = dcc.Graph(id="graph", figure=fig)
        return (
            message,
            content,
        )
    else:
        return html.Div(
            dbc.Alert(id="total-message", children="No records",color="info"),
        )
