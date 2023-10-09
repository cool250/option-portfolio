import logging

import dash_bootstrap_components as dbc
from dash import Dash

from config.settings import LOG_LEVEL

logging.basicConfig(
    format="%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s %(funcName)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    filename="app.log",
    level=LOG_LEVEL,
)

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.LUX, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True,
)
app.title = "Options Tracker"

server = app.server
