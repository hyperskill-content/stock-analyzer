"""
Workflow Service Module
Orchestrates high-level workflows for the Stock Analyzer assistant, including
stock data retrieval, analysis operations, response handling....
"""

# Imports
from colorama import Fore, Style
from config.constants import MessageRole
from services.thread_service import add_message, run_thread


# Functions
def retrieve_stock_data(client, assistant, thread, available_functions):
    """
    Retrieve stock market data for a specified symbol.
    Sends a user prompt to the assistant requesting monthly time series data
    for AAPL stock for the latest 3 months. Executes the run with function
    calling support to fetch data from Alpha Vantage API.
    :param client: The OpenAI client instance
    :param assistant: The assistant object to use for processing
    :param thread: The thread object for conversation context
    :param available_functions: Dictionary mapping function names to callable functions
    :return: The completed run object
    """
    user_prompt_retrieval = "Retrieve the monthly time series data for the stock symbol 'AAPL' for the latest 3 months."
    add_message(client, thread.id, MessageRole.USER, user_prompt_retrieval)
    print()
    print(f"{Fore.CYAN}User message: {Fore.WHITE}{user_prompt_retrieval}{Style.RESET_ALL}")
    print()

    # Execute run with function calling support
    run = run_thread(client, assistant.id, thread.id, available_functions)
    return run


def analyze_stock_data(client, assistant, thread, available_functions):
    """
    Analyze retrieved stock data and display insights.
    Sends a user prompt to the assistant requesting analysis of the previously
    retrieved stock data. The assistant uses Code Interpreter to calculate
    metrics, identify trends, and provide detailed analysis. Displays the
    formatted response if the run completes successfully.
    :param client: The OpenAI client instance
    :param assistant: The assistant object to use for processing
    :param thread: The thread object for conversation context
    :param available_functions: Dictionary mapping function names to callable functions
    """
    user_prompt_analysis = "Analyze the retrieved stock data and identify any trends, calculate ratios, key metrics, etc."
    add_message(client, thread.id, MessageRole.USER, user_prompt_analysis)
    print()
    print(f"{Fore.CYAN}User message: {Fore.WHITE}{user_prompt_analysis}{Style.RESET_ALL}")
    print()
    run = run_thread(client, assistant.id, thread.id, available_functions)

    # Retrieve and display the assistant's response
    if run.status == "completed":
        response_text = get_assistant_response(client, thread.id)
        if response_text:
            print()
            print("=" * 60)
            print(f"{Fore.GREEN}Assistant Response:{Style.RESET_ALL}")
            print("=" * 60)
            print(f"{Fore.WHITE}{response_text}{Style.RESET_ALL}")
            print()


def get_assistant_response(client, thread_id):
    """
    Get the latest assistant message from a thread.
    Retrieves all messages from the specified thread, filters for assistant
    messages, and returns the most recent one. Also adds the response back
    to the thread for conversation continuity.
    :param client: The OpenAI client instance
    :param thread_id: The thread's unique identifier
    :return: The response text from the assistant, or None if no messages found
    """
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    assistant_messages = [msg for msg in messages.data if msg.role == "assistant"]

    if assistant_messages:
        latest_message = assistant_messages[0]
        response_text = latest_message.content[0].text.value
        add_message(client, thread_id, MessageRole.ASSISTANT, response_text)
        return response_text
    return None
