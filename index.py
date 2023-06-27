import os
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output


from app import app
from view import income_finder, oauth, portfolio, analysis, report, home

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
    ],
    brand="Option Guru",
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
    # If the user tries to reach a different page, return a 404 message
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


port = int(os.environ.get("PORT", 8080))
# Adding Host
if __name__ == "__main__":
    app.run(debug=True, port=port)
