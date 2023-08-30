import logging

import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from dotenv import find_dotenv, load_dotenv
from flask_caching import Cache

load_dotenv(find_dotenv()) # read local .env file

# loads the "lux" template and sets it as the default
load_figure_template("bootstrap")

logging.basicConfig(
    filename="app.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(message)s",
)

# Keep this out of source code repository - save in a file or a database
VALID_USERNAME_PASSWORD_PAIRS = [["hello", "nishant"]]

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.LUX],
    suppress_callback_exceptions=True,
)

cache = Cache(
    app.server,
    config={
        "CACHE_TYPE": "filesystem",
        "CACHE_DIR": "cache-directory",
        "CACHE_THRESHOLD": 50,  # should be equal to maximum number of active users
    },
)


app.title = "Options Tracker"
# auth = dash_auth.BasicAuth(
#     app,
#     VALID_USERNAME_PASSWORD_PAIRS
# )
