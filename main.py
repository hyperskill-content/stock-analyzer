"""
Main entry point for Stock Analyzer.

Demonstrates assistant setup, thread creation, message handling,
and run execution using the OpenAI Assistants API.
"""

# Imports
from colorama import Fore, Style, init
from config.constants import ASSISTANT_USER_MESSAGE, MessageRole, AlphaVantageFunctions, \
    ALPHA_VANTAGE_DEFAULT_STOCK_SYMBOL, AlphaVantageIntervals
from services.assistant_service import get_assistant
from services.openai_client import get_client
from services.thread_service import get_thread, add_message, run_thread
from services.stock_service import get_stock_data

# Init
init(autoreset=True)


# My Main
def main():
    print()
    print("=" * 40)
    print(f"{Fore.CYAN}      TASK 1: Assistant Creation{Style.RESET_ALL}")
    print("=" * 40)
    print()

    client = get_client()
    assistant = get_assistant(client)
    thread = get_thread(client)
    message = add_message(client, thread.id, MessageRole.USER, ASSISTANT_USER_MESSAGE)
    run = run_thread(client, assistant.id, thread.id)
    stock_response = get_stock_data(AlphaVantageFunctions.TIME_SERIES_INTRADAY, ALPHA_VANTAGE_DEFAULT_STOCK_SYMBOL,
                                    AlphaVantageIntervals.MIN_5)

    print()
    print("=" * 40)
    print(f"{Fore.CYAN}      TASK 1 Complete{Style.RESET_ALL}")
    print("=" * 40)
    print()


# Execution guard
if __name__ == "__main__":
    main()
