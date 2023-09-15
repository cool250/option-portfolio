import os

from utils.config import ConfigManager

REDIRECT_URI = os.getenv("REDIRECT_URI")


class UserConfig:
    ACCOUNT_NUMBER = ConfigManager.getInstance().getConfig("primary", "ACCOUNT_NUMBER")
    CONSUMER_ID = ConfigManager.getInstance().getConfig("primary", "CONSUMER_ID")
