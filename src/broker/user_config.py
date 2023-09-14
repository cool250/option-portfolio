import os

REDIRECT_URI = os.getenv("REDIRECT_URI")


class UserConfig:
    ACCOUNT_NUMBER = os.getenv("ACCOUNT_NUMBER")
    CONSUMER_ID = os.getenv("CONSUMER_ID")
