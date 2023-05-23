import logging

import dash
import dash_bootstrap_components as dbc
from flask_caching import Cache
import plotly.io as pio
pio.templates.default = "simple_white"

logging.basicConfig(filename="app.log",
                    level=logging.DEBUG, format='%(asctime)s - %(name)s - %(message)s')

# Keep this out of source code repository - save in a file or a database
VALID_USERNAME_PASSWORD_PAIRS = [
    ['hello', 'nishant']
]

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.COSMO],
    suppress_callback_exceptions=True,
    prevent_initial_callbacks="initial_duplicate",
)

cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory',
    'CACHE_THRESHOLD': 50  # should be equal to maximum number of active users
})



app.title = 'Options Tracker'
# auth = dash_auth.BasicAuth(
#     app,
#     VALID_USERNAME_PASSWORD_PAIRS
# )
