import dash_bootstrap_components as dbc
import dash_tabulator
from dash import dcc, html
from dash.dependencies import Input, Output, State

from app import app
from service.account_transactions import get_report

# downloadButtonType
# takes
#       css     => class names
#       text    => Text on the button
#       type    => type of download (csv/ xlsx / pdf, remember to include appropriate 3rd party js libraries)
#       filename => filename prefix defaults to data, will download as filename.type

TOP_COLUMN = dbc.Form(
    [
        dbc.Row(
            [
                dbc.Col(
                    children=[
                        dbc.Label("From Date", size="sm"),
                        dbc.Col(
                            dcc.DatePickerSingle(
                                id="start-date-picker",
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
                                id="end-date-picker",
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
                            id="report-ticker",
                            placeholder="symbol",
                            size="sm",
                        ),
                    ],
                ),
                dbc.Col(
                    children=[
                        dbc.Label("Instrument Type", size="sm"),
                        dbc.Select(
                            id="instrument-type",
                            options=[
                                {"label": "CALL", "value": "CALL"},
                                {"label": "PUT", "value": "PUT"},
                                {"label": "EQUITY", "value": "EQUITY"},
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
                            id="report-btn",
                            className="mt-4",
                        ),
                    ]
                ),
            ],
        ),
    ],
    className="p-2 bg-light border",
)

SEARCH_RESULT = html.Div(
    [
        dbc.Alert(
            id="report-message",
            is_open=False,
        ),
        dbc.Spinner(html.Div(id="report-output")),
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
downloadButtonType = {"css": "btn btn-secondary mb-3", "text": "Export", "type": "csv"}


@app.callback(
    [
        Output("report-output", "children"),
        Output("report-message", "is_open"),
        Output("report-message", "children"),
    ],
    [
        Input("report-btn", "n_clicks"),
    ],
    [
        State("start-date-picker", "date"),
        State("end-date-picker", "date"),
        State("report-ticker", "value"),
        State("instrument-type", "value"),
    ],
)
def on_search(n, start_date, end_date, ticker, instrument_type):
    if n is None:
        return None, False, ""
    else:
        df = get_report(start_date, end_date, ticker, instrument_type)
        if not df.empty:
            if instrument_type == "EQUITY":
                columns = [
                    {"title": "SYMBOL", "field": "SYMBOL", "headerFilter": "input"},
                    {"title": "DATE", "field": "DATE"},
                    {"title": "PRICE", "field": "PRICE"},
                    {"title": "INSTRUCTION", "field": "INSTRUCTION"},
                    {
                        "title": "TOTAL PRICE",
                        "field": "TOTAL_PRICE",
                        "topCalc": "sum",
                        "topCalcParams": {
                            "precision": 2,
                        },
                    },
                    {"title": "QTY", "field": "QTY"},
                ]
            else:
                columns = [
                    {"title": "TICKER", "field": "TICKER", "headerFilter": "input"},
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
                    {"title": "PRICE", "field": "PRICE"},
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
                    downloadButtonType=downloadButtonType,
                ),
            )

            return dt, False, ""
        else:
            return None, True, "No Records found"
