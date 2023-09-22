from flask_caching import Cache

from app import app

cache = Cache(
    app.server,
    config={
        "CACHE_TYPE": "filesystem",
        "CACHE_DIR": "cache-directory",
        "CACHE_THRESHOLD": 50,  # should be equal to maximum number of active users
    },
)
