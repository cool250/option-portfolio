# multiplotter
import numpy as np
import plotly.graph_objects as go

from .helpers import payoff_calculator, check_optype, check_trtype

abb = {"c": "Call", "p": "Put", "e": "Equity", "b": "Long", "s": "Short"}


def multi_plotter(
    spot,
    op_list,
    spot_range=5,
):
    """
    Plots a basic option payoff diagram for a multiple options and resultant payoff diagram

    Parameters
    ----------
    spot: int, float, default: 100
       Spot Price

    spot_range: int, float, optional, default: 20
       Range of spot variation in percentage

    op_list: list of dictionary

       Each dictionary must contiain following keys
       'strike': int, float, default: 720
           Strike Price
       'tr_type': kind {'b', 's'} default:'b'
          Transaction Type>> 'b': long, 's': short
       'op_pr': int, float, default: 10
          Option Price
       'op_type': kind {'c','p'}, default:'c'
          Opion type>> 'c': call option, 'p':put option
       'contracts': int default:1, optional
           Number of contracts

    save: Boolean, default False
        Save figure

    file: String, default: 'fig.png'
        Filename with extension

    Example
    -------
    op1={'op_type':'c','strike':110,'tr_type':'s','op_pr':2,'contract':1}
    op2={'op_type':'p','strike':95,'tr_type':'s','op_pr':6,'contract':1}

    import opstrat  as op
    op.multi_plotter(spot_range=20, spot=100, op_list=[op1,op2])

    #Plots option payoff diagrams for each op1 and op2 and combined payoff

    """
    x = spot * np.arange(100 - spot_range, 101 + spot_range, 0.01) / 100
    y0 = np.zeros_like(x)

    y_list = []
    for op in op_list:
        op_type = str.lower(op["op_type"])
        tr_type = str.lower(op["tr_type"])
        check_optype(op_type)
        check_trtype(tr_type)

        strike = op["strike"]
        op_pr = op["op_pr"]
        try:
            contract = op["contract"]
        except:
            contract = 1
        y_list.append(payoff_calculator(x, op_type, strike, op_pr, tr_type, contract))


    def plotly_plot():
        fig = go.Figure()
        y = 0
        for i in range(len(op_list)):
            try:
                contract = str(op_list[i]["contract"])
            except:
                contract = "1"

            label = (
                contract
                + " "
                + str(abb[op_list[i]["tr_type"]])
                + " "
                + str(abb[op_list[i]["op_type"]])
                + " ST: "
                + str(op_list[i]["strike"])
            )
            fig.add_trace(go.Scatter(x=x, y=y_list[i], name=label))
            y += np.array(y_list[i])

        fig.add_trace(go.Scatter(x=x, y=y, name="combined"))
        fig.add_vline(
            x=spot, line_dash="dash", line_color="blue", annotation_text="spot price"
        )
        fig.add_hline(y=0, line_dash="dash", line_color="black")

        # Edit the layout
        fig.update_layout(
            title="Options Payoff", xaxis_title="Strike Price", yaxis_title="Premium"
        )
        return fig

    fig = plotly_plot()
    return fig
