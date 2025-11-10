"""
Main entry point for Stock Analyzer.

Demonstrates assistant setup, thread creation, message handling,
and run execution using the OpenAI Assistants API.
"""

# Imports
from colorama import init
from config.constants import AlphaVantageAvailableFunctions
from services.assistant_service import get_assistant
from services.openai_client import get_client
from services.thread_service import get_thread
from services.stock_service import get_stock_data
from services.workflow_service import analyze_stock_data, retrieve_stock_data
from main_helpers import main_initialization, main_end

# Init
init(autoreset=True)


# Main Function
def main():
    # Welcome message
    main_initialization()

    # Initialize client and assistant
    client = get_client()
    assistant = get_assistant(client)
    thread = get_thread(client)

    # Available functions that the assistant can call
    available_functions = {
        AlphaVantageAvailableFunctions.GET_STOCK_DATA.value: get_stock_data
    }

    # Retrieve and analysis stock data
    retrieve_stock_data(client, assistant, thread, available_functions)
    analyze_stock_data(client, assistant, thread, available_functions)

    # Finish message
    main_end()


# Execution guard
if __name__ == "__main__":
    main()
