from .base import Base
from .domain_objects import Balance, Position, SecuritiesAccount
from .urls import GET_ACCOUNT, GET_ACCOUNTS


class Account(Base):

    """A class for searching for an account."""

    def __init__(self, **query):
        Base.__init__(self)

    def get_accounts(self, account="all", fields=None):
        """
        Serves as the mechanism to make a request to the "Get Accounts" and "Get Account" Endpoint.
        If one account is provided a "Get Account" request will be made and if more than one account
        is provided then a "Get Accounts" request will be made.

        Documentation Link: https://developer.tdameritrade.com/account-access/apis

        NAME: account
        DESC: The account number you wish to recieve data on. Default value is 'all'
              which will return all accounts of the user.
        TYPE: String

        NAME: fields
        DESC: Balances displayed by default, additional fields can be added here by
              adding positions or orders.
        TYPE: List<String>

        EXAMPLES:

        SessionObject.get_accounts(account = 'all', fields = ['orders'])
        SessionObject.get_accounts(account = 'MyAccountNumber', fields = ['orders','positions'])

        """
        # because we have a list argument, prep it for the request.
        fields = self.prepare_arguments_list(parameter_list=fields)

        # build the params dictionary
        data = {"apikey": self.config["consumer_id"], "fields": fields}

        # if all use '/accounts' else pass through the account number.
        if account == "all":
            endpoint = GET_ACCOUNTS
        else:
            endpoint = GET_ACCOUNT.format(accountId=account)

        # build the url
        url = self.api_endpoint(endpoint)

        self._data = self._api_response(url=url, params=data, verify=True)

        # return the response of the get request.
        return self._data

    def get_positions(self):
        # a dictionary is returned if there is only one position, so convert it to list.
        if type(self._positionkey) is dict:
            self._positionkey = [self._positionkey]
        positions = []
        for position in self._positionkey:
            if position["shortQuantity"]:
                quantity = position["settledShortQuantity"]
            else:
                quantity = position["settledLongQuantity"]
            try:
                underlying = position["instrument"]["underlyingSymbol"]
            except KeyError:
                underlying = position["instrument"]["symbol"]
            if position["instrument"]["assetType"] == "OPTION":
                option_type = position["instrument"]["putCall"]
            else:
                option_type = None
            new_position = Position(
                quantity=quantity,
                symbol=position["instrument"]["symbol"],
                instrument_type=position["instrument"]["assetType"],
                underlying=underlying,
                option_type=option_type,
                averagePrice=position["averagePrice"],
                maintenanceRequirement=position["maintenanceRequirement"],
            )
            positions.append(new_position)
        return positions
    
    def get_balances(self):
        balance = Balance()
        balance.marginBalance =  self._balanceskey["cashBalance"]
        balance.maintenanceRequirement = self._balanceskey["maintenanceRequirement"]
        balance.accountValue = self._balanceskey["liquidationValue"]
        return balance

    
    def get_portfolio(self, account="all"):
        self.get_accounts(account, fields=["positions"])
        try:
            self._positionkey = self._data["securitiesAccount"]["positions"]
            self._balanceskey = self._data["securitiesAccount"]["currentBalances"]
        except KeyError:
            return None
        
        positions = self.get_positions()
        balance = self.get_balances()
        return SecuritiesAccount(balance, positions)
