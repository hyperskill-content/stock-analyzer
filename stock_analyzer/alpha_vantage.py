import os

import requests

functions_list = [
    {
        "type": "function",
        "function": {
            "name": "get_time_series",
            "description": "Get time series stock data",
            "parameters": {
                "type": "object",
                "properties": {
                    "function": {
                        "type": "string",
                        "description": "The time series of your choice",
                        "enum": ["TIME_SERIES_INTRADAY", "TIME_SERIES_DAILY", "TIME_SERIES_WEEKLY",
                                 "TIME_SERIES_MONTHLY"]
                    },
                    "symbol": {
                        "type": "string",
                        "description": "The name of the equity of your choice. For example: `symbol=IBM`"
                    },
                    "interval": {
                        "type": "string",
                        "description": "Time interval between two consecutive data points in the time series. Only with function `TIME_SERIES_INTRADAY`.",
                        "enum": ["1min", "5min", "15min", "30min", "60min"]
                    }
                },
                "required": ["function", "symbol"],
            },
        },
    }
]


def get_time_series(function, symbol, api_key=None, interval=None):
    if api_key is None:
        api_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
    params = {"function": function, "symbol": symbol, "apikey": api_key}
    if interval:
        params["interval"] = interval
    return requests.get(f"https://www.alphavantage.co/query", params=params)


def name_to_function(name):
    return {"get_time_series": get_time_series}.get(name)
