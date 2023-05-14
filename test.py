import opstrat as op
import plotly.graph_objects as go
import plotly.express as px

op_1 = {'op_type':'c','strike':'420','tr_type':'s','op_pr':3.27}
op_2 = {'op_type':'p','strike':'400','tr_type':'s','op_pr':3.02}
op_3 = {'op_type':'c','strike':'425','tr_type':'b','op_pr':1.53}
fig = op.multi_plotter(spot=412, op_list=[op_1,op_2, op_3])

fig.show()

