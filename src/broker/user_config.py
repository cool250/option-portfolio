import os

from utils.config import Config

REDIRECT_URI = os.getenv("REDIRECT_URI")


class UserConfig:
    ACCOUNT_NUMBER = Config().get("primary", "ACCOUNT_NUMBER")
    CONSUMER_ID = Config().get("primary", "CONSUMER_ID")
