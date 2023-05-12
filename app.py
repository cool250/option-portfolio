import logging

import dash
import dash_auth
import dash_bootstrap_components as dbc

logging.basicConfig(filename="app.log",
                    level=logging.DEBUG, format='%(asctime)s %(funcName)s %(message)s')

# Keep this out of source code repository - save in a file or a database
VALID_USERNAME_PASSWORD_PAIRS = [
    ['hello', 'nishant']
]

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.COSMO],
    suppress_callback_exceptions=True
)

app.title = 'Options Tracker'
# auth = dash_auth.BasicAuth(
#     app,
#     VALID_USERNAME_PASSWORD_PAIRS
# )
