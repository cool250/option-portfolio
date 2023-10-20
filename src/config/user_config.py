import os

from utils.accounts import Accounts

REDIRECT_URI = "http://localhost"


class UserConfig:
    ACCOUNT_NUMBER = Accounts().get_default_account_number()
    CONSUMER_ID = Accounts().get_default_consumer_id()
