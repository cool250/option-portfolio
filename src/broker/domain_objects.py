class Position:
	def __init__(self, quantity, symbol, instrument_type, underlying, option_type, averagePrice, maintenanceRequirement):
		self.quantity = quantity
		self.symbol = symbol
		self.instrument_type = instrument_type
		self.underlying = underlying
		self.option_type = option_type
		self.averagePrice = averagePrice
		self.maintenanceRequirement = maintenanceRequirement

class Balance:
	def __init__(self, marginBalance=0, maintenanceRequirement=0, liquidationValue=0):
		self.marginBalance = marginBalance
		self.maintenanceRequirement = maintenanceRequirement
		self.accountValue = liquidationValue

class SecuritiesAccount:
	def __init__(self, balance, positions,):
		self.positions = positions
		self.balance = balance

		

