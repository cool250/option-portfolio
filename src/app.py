import logging
import os

import dash_bootstrap_components as dbc
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import load_figure_template
from dotenv import find_dotenv, load_dotenv

from broker.user_config import UserConfig
from utils.accounts import Accounts
from view import home, income_finder, oauth, portfolio, report, trade_chart

load_dotenv(find_dotenv())  # read local .env file

debug = False if os.environ["DASH_DEBUG_MODE"] == "False" else True

# loads the "lux" template and sets it as the default
load_figure_template("bootstrap")

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.LUX, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True,
)
app.title = "Options Tracker"

server = app.server

logging.basicConfig(
    format="%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s %(funcName)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    filename="app.log",
    level=logging.INFO,
)

user_bar = dbc.DropdownMenu(
    [
        dbc.DropdownMenuItem(account, href=account)
        for account in Accounts().get_account_list()
    ],
    label=html.I(className="fa-regular fa-user"),
)


navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(
            dbc.NavLink("Home", href="/home", id="page-1-link", class_name="nav-link")
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
                "Stock_Scan", href="/chart", id="page-6-link", class_name="nav-link"
            )
        ),
        dbc.NavItem(
            dbc.NavLink(
                "Options_Scan",
                href="/income_finder",
                id="page-2-link",
                class_name="nav-link",
            )
        ),
        user_bar,
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
    elif pathname == "/chart":
        return trade_chart.layout
    # User switch from DropdownMenu
    elif pathname == "/brokerage":
        UserConfig.ACCOUNT_NUMBER = Accounts().get_account_number("brokerage")
        UserConfig.CONSUMER_ID = Accounts().get_consumer_id("brokerage")
        raise PreventUpdate
    elif pathname == "/ira":
        UserConfig.ACCOUNT_NUMBER = Accounts().get_account_number("ira")
        UserConfig.CONSUMER_ID = Accounts().get_consumer_id("ira")
        raise PreventUpdate
    # If the user tries to reach a different page, return a 404 message
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


port = int(os.environ.get("SERVER_PORT", 8080))
# Adding Host
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=port, use_reloader=False)
