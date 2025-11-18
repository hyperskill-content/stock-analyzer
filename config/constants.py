"""
Configuration constants for the Stock Analyzer Assistant.

Contains assistant configuration, model settings, and enumerations
for message roles used throughout the application.
"""

from enum import Enum

# Assistant Configuration
ASSISTANT_MODEL = "gpt-4o-mini"
ASSISTANT_NAME = "stock_analyzer_assistant"
ASSISTANT_INSTRUCTION = "You're an experienced stock analyzer assistant tasked with analyzing and visualizing stock market data."
ASSISTANT_USER_MESSAGE = "Tell me your name and instructions. YOU MUST Provide a DIRECT and SHORT response."


class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"


# Alpha Vantage API Configuration
class AlphaVantageFunctions(Enum):
    TIME_SERIES_INTRADAY = "TIME_SERIES_INTRADAY"
    TIME_SERIES_DAILY = "TIME_SERIES_DAILY"
    TIME_SERIES_WEEKLY = "TIME_SERIES_WEEKLY"
    TIME_SERIES_MONTHLY = "TIME_SERIES_MONTHLY"


class AlphaVantageIntervals(Enum):
    MIN_1 = "1min"
    MIN_5 = "5min"
    MIN_15 = "15min"
    MIN_30 = "30min"
    MIN_60 = "60min"


class AlphaVantageAvailableFunctions(Enum):
    GET_STOCK_DATA = "get_stock_data"


ALPHA_VANTAGE_BASE_QUERY_URL = "https://www.alphavantage.co/query"
ALPHA_VANTAGE_DEFAULT_INTERVAL = AlphaVantageIntervals.MIN_5
ALPHA_VANTAGE_DEFAULT_STOCK_SYMBOL = "AAPL"

# Thread Run Configuration
THREAD_RUN_TIMEOUT_SECONDS = 300  # 5 minutes max for run completion
THREAD_RUN_POLL_INTERVAL_SECONDS = 20  # Check status every 20 seconds
