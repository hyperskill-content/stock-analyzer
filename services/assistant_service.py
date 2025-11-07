"""
Assistant management service.

Handles creation and retrieval of OpenAI assistants for stock analysis.
"""

# Imports
from colorama import Fore, Style
from config.constants import ASSISTANT_NAME, ASSISTANT_INSTRUCTION, ASSISTANT_MODEL


# Function
def get_assistant(client):
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
        return matching_assistant
    else:
        try:
            new_assistant = client.beta.assistants.create(
                name=ASSISTANT_NAME,
                instructions=ASSISTANT_INSTRUCTION,
                model=ASSISTANT_MODEL
            )
            print(f"{Fore.GREEN}Created new assistant with ID: {Fore.YELLOW}{new_assistant.id}{Style.RESET_ALL}")
            return new_assistant
        except Exception as e:
            print(f"{Fore.RED}Error: Failed to create assistant.{Style.RESET_ALL}")
            print(f"Details: {e}")
            exit(1)
