from dash import dcc, html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import load_figure_template

from app import app
from components.main_layout import content, navbar
from config.settings import APP_DEBUG, APP_HOST, APP_PORT
from config.user_config import UserConfig
from utils.accounts import Accounts
from view import (
    chatbot_view,
    home,
    income_finder,
    oauth,
    portfolio,
    report,
    trade_chart,
)

# loads the "lux" template and sets it as the default
load_figure_template("bootstrap")
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
    elif pathname == "/chat":
        return chatbot_view.layout
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


# Adding Host
if __name__ == "__main__":
    app.run(debug=APP_DEBUG, host=APP_HOST, port=APP_PORT)
