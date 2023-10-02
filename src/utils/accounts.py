from config.account_reader import JSONReader


class Accounts:
    """
    Accounts:
    This class uses the JSONReader to load account data from a JSON file.
    """

    def __init__(self):
        json_file_path = "accounts.json"
        self.json_reader = JSONReader(json_file_path)

    def get_account_list(self):
        account_names = [i for i in self.json_reader.data]
        return account_names

    def get_account_number(self, account):
        return self.json_reader.data[account]["account_number"]

    def get_consumer_id(self, account):
        return self.json_reader.data[account]["consumer_id"]

    def get_default_account_number(self):
        first_account_number = None

        for account_type, account_info in self.json_reader.data.items():
            if "account_number" in account_info:
                first_account_number = account_info["account_number"]
                return first_account_number

    def get_default_consumer_id(self):
        first_consumer_id = None

        for account_type, account_info in self.json_reader.data.items():
            if "account_number" in account_info:
                first_consumer_id = account_info["consumer_id"]
                return first_consumer_id
