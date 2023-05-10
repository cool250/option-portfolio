import opstrat as op
import plotly.graph_objects as go
from service.spread_screen import search_spreads
import plotly.express as px

# op_1 = {'op_type':'c','strike':420,'tr_type':'s','op_pr':3.27}
# op_2 = {'op_type':'p','strike':400,'tr_type':'s','op_pr':3.02}
# op_3 = {'op_type':'c','strike':425,'tr_type':'b','op_pr':1.53}
# op.multi_plotter(spot=412, op_list=[op_1,op_2, op_3])


df = search_spreads("SPY")
print(df)