"""
Stock data retrieval service.

Handles fetching stock market data from the Alpha Vantage API
for various time series intervals (intraday, daily, weekly, monthly).
"""

# Imports
from colorama import Fore, Style
from config.settings import settings
from config.constants import ALPHA_VANTAGE_BASE_QUERY_URL, ALPHA_VANTAGE_DEFAULT_INTERVAL, AlphaVantageFunctions, \
    AlphaVantageIntervals
from typing import Union, Dict, Any
import requests


# Functions
def get_stock_data(function: Union[AlphaVantageFunctions, str], symbol: str,
                   interval: Union[AlphaVantageIntervals, str] = ALPHA_VANTAGE_DEFAULT_INTERVAL) -> Dict[str, Any]:
    """
    Fetch stock data from Alpha Vantage API
    :param function: One of the time series functions
    :param symbol: Stock symbol (e.g., 'AAPL')
    :param interval: Time interval for intraday data (e.g., '5min', '15min', '60min')
    :return: Stock data JSON response
    """
    alphavantage_api_key = settings.alpha_vantage_api_key

    # Extract .value if enums, otherwise use it directly
    function_value = function.value if hasattr(function, 'value') else function
    interval_value = interval.value if hasattr(interval, 'value') else interval

    try:
        query_url = f"{ALPHA_VANTAGE_BASE_QUERY_URL}?function={function_value}&symbol={symbol}&apikey={alphavantage_api_key}"
        if function_value == AlphaVantageFunctions.TIME_SERIES_INTRADAY.value:
            query_url += f"&interval={interval_value}"

        response = requests.get(query_url)
        response.raise_for_status()
        response_json = response.json()
        print(f"{Fore.GREEN}Called Alpha Vantage Stock with Symbol: {Fore.YELLOW}{symbol}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Response Json: {Fore.YELLOW}{str(response_json)[:90]}...{Style.RESET_ALL}")
        return response_json
    except requests.RequestException as e:
        print(f"{Fore.RED}Error: Failed to fetch stock data for {symbol}.{Style.RESET_ALL}")
        print(f"Details: {e}")
        return {}
