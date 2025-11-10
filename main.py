"""
Main entry point for Stock Analyzer.

Demonstrates assistant setup, thread creation, message handling,
and run execution using the OpenAI Assistants API.
"""

# Imports
from colorama import Fore, Style, init
from config.constants import MessageRole, AlphaVantageAvailableFunctions
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
    print(f"{Fore.CYAN}      TASK 2: Data Retrieval{Style.RESET_ALL}")
    print("=" * 40)
    print()

    # Initialize client and assistant
    client = get_client()
    assistant = get_assistant(client)
    thread = get_thread(client)

    # User prompt to trigger function calling
    user_prompt = "Retrieve and show the latest daily time series data for the stock symbol 'AAPL'."
    message = add_message(client, thread.id, MessageRole.USER, user_prompt)
    print(f"{Fore.CYAN}User message: {Fore.WHITE}{user_prompt}{Style.RESET_ALL}")
    print()

    # Available functions that the assistant can call
    available_functions = {
        AlphaVantageAvailableFunctions.GET_STOCK_DATA.value: get_stock_data
    }

    # Execute run with function calling support
    run = run_thread(client, assistant.id, thread.id, available_functions)

    # Retrieve and display the assistant's response
    if run.status == "completed":
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        assistant_messages = [msg for msg in messages.data if msg.role == "assistant"]

        if assistant_messages:
            latest_message = assistant_messages[0]
            response_text = latest_message.content[0].text.value
            print()
            print("=" * 60)
            print(f"{Fore.GREEN}Assistant Response:{Style.RESET_ALL}")
            print("=" * 60)
            print(f"{Fore.WHITE}{response_text}{Style.RESET_ALL}")
            print()

    print()
    print("=" * 40)
    print(f"{Fore.CYAN}      TASK 2 Complete{Style.RESET_ALL}")
    print("=" * 40)
    print()


# Execution guard
if __name__ == "__main__":
    main()
