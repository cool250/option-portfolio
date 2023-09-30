import dash_bootstrap_components as dbc
from dash import html

from utils.accounts import Accounts

# Create a DropdownMenu for user account selection
user_bar = dbc.DropdownMenu(
    [
        dbc.DropdownMenuItem(account, href=account)
        for account in Accounts().get_account_list()
    ],
    label=html.I(className="fa-regular fa-user"),
)

# Create a navigation bar for the application
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(
            dbc.NavLink("Home", href="/home", id="page-1-link", class_name="nav-link")
        ),
        dbc.NavItem(
            dbc.NavLink(
                "Portfolio", href="/portfolio", id="page-2-link", class_name="nav-link"
            )
        ),
        dbc.NavItem(
            dbc.NavLink(
                "Report", href="/report", id="page-3-link", class_name="nav-link"
            )
        ),
        dbc.NavItem(
            dbc.NavLink(
                "Stock_Scan", href="/chart", id="page-4-link", class_name="nav-link"
            )
        ),
        dbc.NavItem(
            dbc.NavLink(
                "Options_Scan",
                href="/income_finder",
                id="page-5-link",
                class_name="nav-link",
            )
        ),
        dbc.NavItem(
            dbc.NavLink("Chat", href="/chat", id="page-6-link", class_name="nav-link")
        ),
        user_bar,
    ],
    brand="Options Guru",  # Brand name for the navigation bar
    brand_href="#",  # Brand link (currently set to "#")
    color="primary",  # Navbar color
    dark=True,  # Use dark theme for the navbar
)

# Create a content container for the application pages
content = html.Div(id="page-content", className="p-3")
