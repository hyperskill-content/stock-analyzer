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
        response_text, image_file_id = get_assistant_response(client, thread.id)
        if response_text:
            print()
            print(f"{Fore.GREEN}Assistant Response:{Style.RESET_ALL}")
            print(f"{Fore.WHITE}{response_text}{Style.RESET_ALL}")
            print()
        if image_file_id:
            print(f"{Fore.GREEN}Assistant Response Image file ID: {image_file_id}{Style.RESET_ALL}")
            print()


def visualize_stock_data(client, assistant, thread, available_functions):
    """
    Visualize stock market data with charts.
    Sends a prompt to the assistant to create visual representations of stock data.
    Downloads and saves the generated chart as stock-image.png.
    """
    user_prompt_visualization = "Retrieve and visualize the monthly time series data for the stock symbol 'AAPL' for the latest 12 months."
    add_message(client, thread.id, MessageRole.USER, user_prompt_visualization)
    print()
    print(f"{Fore.CYAN}User message: {Fore.WHITE}{user_prompt_visualization}{Style.RESET_ALL}")
    print()
    run = run_thread(client, assistant.id, thread.id, available_functions)

    # Retrieve and display the assistant's response
    if run.status == "completed":
        response_text, image_file_id = get_assistant_response(client, thread.id)
        if response_text:
            print()
            print(f"{Fore.GREEN}Assistant Response:{Style.RESET_ALL}")
            print(f"{Fore.WHITE}{response_text}{Style.RESET_ALL}")
            print()
        if image_file_id:
            print(f"{Fore.GREEN}Assistant Response Image file ID: {image_file_id}{Style.RESET_ALL}")
            print()

            # Download and save the image
            try:
                file_content = client.files.content(image_file_id)
                image_data = file_content.read()
                with open("stock-image.png", "wb") as file:
                    file.write(image_data)
                print(f"{Fore.GREEN}Image saved as stock-image.png{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}Error saving image: {e}{Style.RESET_ALL}")
            print()


def get_assistant_response(client, thread_id):
    """
    Get the latest assistant message from a thread.
    Retrieves all messages from the specified thread, filters for assistant
    messages, and returns the most recent one.
    :param client: The OpenAI client instance
    :param thread_id: The thread's unique identifier
    :return: The response text from the assistant, or None if no messages are found
    """
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    assistant_messages = [msg for msg in messages.data if msg.role == "assistant"]

    if assistant_messages:
        latest_message = assistant_messages[0]
        response_text = ""
        image_file_id = None

        # Loop through ALL content blocks
        for content_block in latest_message.content:
            if content_block.type == "text":
                response_text += content_block.text.value
            elif content_block.type == "image_file":
                image_file_id = content_block.image_file.file_id

        return response_text, image_file_id
    return None, None
