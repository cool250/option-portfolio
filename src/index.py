import logging
import os

import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
from dash_bootstrap_templates import load_figure_template
from dotenv import find_dotenv, load_dotenv

from app import app
from view import analysis, home, income_finder, oauth, portfolio, report, trade_chart

load_dotenv(find_dotenv())  # read local .env file

# loads the "lux" template and sets it as the default
load_figure_template("bootstrap")

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(message)s",
)

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(
            dbc.NavLink("Home", href="/home", id="page-1-link", class_name="nav-link")
        ),
        dbc.NavItem(
            dbc.NavLink(
                "Scanner",
                href="/income_finder",
                id="page-2-link",
                class_name="nav-link",
            )
        ),
        dbc.NavItem(
            dbc.NavLink(
                "Portfolio", href="/portfolio", id="page-3-link", class_name="nav-link"
            )
        ),
        dbc.NavItem(
            dbc.NavLink(
                "Report", href="/report", id="page-4-link", class_name="nav-link"
            )
        ),
        dbc.NavItem(
            dbc.NavLink(
                "Analysis", href="/analysis", id="page-5-link", class_name="nav-link"
            )
        ),
        dbc.NavItem(
            dbc.NavLink("Chart", href="/chart", id="page-6-link", class_name="nav-link")
        ),
    ],
    brand="Options Guru",
    brand_href="#",
    color="primary",
    dark=True,
)

content = html.Div(id="page-content", className="p-3")


app.layout = html.Div([dcc.Location(id="url"), navbar, content])


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/home"]:
        return home.layout
    elif pathname == "/income_finder":
        return income_finder.layout
    elif pathname == "/portfolio":
        return portfolio.layout
    elif pathname == "/report":
        return report.layout
    elif pathname == "/oauth":
        return oauth.layout
    elif pathname == "/dashboard":
        return report.layout
    elif pathname == "/analysis":
        return analysis.layout
    elif pathname == "/chart":
        return trade_chart.layout
    # If the user tries to reach a different page, return a 404 message
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


port = int(os.environ.get("SERVER_PORT", 80))
# Adding Host
if __name__ == "__main__":
    app.run(debug=True, port=port)
