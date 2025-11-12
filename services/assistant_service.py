"""
Assistant management service.

Handles creation and retrieval of OpenAI assistants for stock analysis.
"""

# Imports
from colorama import Fore, Style
from config.constants import ASSISTANT_NAME, ASSISTANT_INSTRUCTION, ASSISTANT_MODEL, AlphaVantageAvailableFunctions
from openai import OpenAI

# Tools
get_stock_data_tool = {
    "type": "function",
    "function": {
        "name": AlphaVantageAvailableFunctions.GET_STOCK_DATA.value,
        "description": "Fetch stock market time series data from Alpha Vantage API. Supports intraday, daily, weekly, and monthly data.",
        "parameters": {
            "type": "object",
            "properties": {
                "function": {
                    "type": "string",
                    "enum": [
                        "TIME_SERIES_INTRADAY",
                        "TIME_SERIES_DAILY",
                        "TIME_SERIES_WEEKLY",
                        "TIME_SERIES_MONTHLY"
                    ],
                    "description": "Type of time series data to fetch"
                },
                "symbol": {
                    "type": "string",
                    "description": "Stock ticker symbol (e.g., AAPL, GOOGL, MSFT)"
                },
                "interval": {
                    "type": "string",
                    "enum": ["1min", "5min", "15min", "30min", "60min"],
                    "description": "Time interval for intraday data. Only used when function is TIME_SERIES_INTRADAY. Defaults to 5min if not specified."
                }
            },
            "required": ["function", "symbol"]
        }
    }
}

get_code_interpreter_tool = {
    "type": "code_interpreter"
}


# Function
def get_assistant(client: OpenAI) -> object:
    """
    Find an existing Stock Analyzer assistant or create a new one.
    :param client: The OpenAI client instance
    :return: The assistant object (existing or newly created)
    """
    try:
        current_assistants = client.beta.assistants.list()
    except Exception as e:
        print(f"{Fore.RED}Error: Failed to retrieve assistants list.{Style.RESET_ALL}")
        print(f"Details: {e}")
        exit(1)

    matching_assistant = next((a for a in current_assistants.data if a.name == ASSISTANT_NAME), None)
    if matching_assistant:
        print(f"{Fore.GREEN}Found existing assistant with ID: {Fore.YELLOW}{matching_assistant.id}{Style.RESET_ALL}")
        try:
            updated_assistant = client.beta.assistants.update(assistant_id=matching_assistant.id,
                                                              tools=[get_code_interpreter_tool, get_stock_data_tool])
            return updated_assistant
        except Exception as e:
            print(f"{Fore.YELLOW}Warning: Could not update assistant tools{Style.RESET_ALL}")
            print(f"Details: {e}")
            return matching_assistant
    else:
        try:
            new_assistant = client.beta.assistants.create(
                name=ASSISTANT_NAME,
                instructions=ASSISTANT_INSTRUCTION,
                model=ASSISTANT_MODEL,
                tools=[get_code_interpreter_tool, get_stock_data_tool]
            )
            print(f"{Fore.GREEN}Created new assistant with ID: {Fore.YELLOW}{new_assistant.id}{Style.RESET_ALL}")
            return new_assistant
        except Exception as e:
            print(f"{Fore.RED}Error: Failed to create assistant.{Style.RESET_ALL}")
            print(f"Details: {e}")
            exit(1)
