import os

from utils.accounts import Accounts

REDIRECT_URI = os.getenv("REDIRECT_URI")


class UserConfig:
    ACCOUNT_NUMBER = Accounts().get_account_number("brokerage")
    CONSUMER_ID = Accounts().get_consumer_id("brokerage")
