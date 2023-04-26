# Creating an empty dictionary
screener_list = {}

# Adding list as value
screener_list["option_stocks"] = [
    "HD",
    "IBM",
    "TGT",
    "MSFT",
    "CRM",
    "FDX",
    "INTC",
    "NFLX",
    "CAT",
    "C",
    "WFC",
    "DIS",
    "NVDA",
    "EA",
    "FB",
    "AAPL",
    "BA",
    "AMD",
    "LYFT",
    "TSLA",
    "TWTR",
    "SPCE",
]
screener_list["finance"] = ["WF", "BAC", "JPM", "C", "GS", "V", "AXP", "COF"]
screener_list["tech"] = ["ORCL", "IBM", "FB", "AAPL", "NFLX", "MSFT", "QQQ", "TWTR"]
screener_list["ETF"] = [
    "XLE",
    "VTE",
    "XLB",
    "XLI",
    "XLY",
    "XLP",
    "XLF",
    "XLV",
    "XLU",
    "DIA",
    "UNG",
    "IEF",
    "TLT",
    "TLT",
    "SQQQ",
    "HYG",
    "EWZ",
    "EEM",
    "VXX",
    "GDX",
    "IWM",
    "GLD",
    "QQQ",
    "SLV",
    "SPY",
]
screener_list["Favorites"] = ["SPY", "QQQ"]

style_cell = {
    "padding": "12px",
    "width": "auto",
    "textAlign": "center",
    "fontFamily": '"Segoe UI", "Source Sans Pro", Calibri, Candara, Arial, sans-serif',
}
style_header = {
    "backgroundColor": "#2C3E50",
    "color": "white",
    "textAlign": "center",
}
style_data_conditional = [
    {
        # stripped rows
        "if": {"row_index": "odd"},
        "backgroundColor": "rgb(248, 248, 248)",
    },
]
