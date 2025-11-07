"""
Main entry point for Stock Analyzer.

Demonstrates assistant setup, thread creation, message handling,
and run execution using the OpenAI Assistants API.
"""

# Imports
from colorama import Fore, Style, init
from config.constants import ASSISTANT_USER_MESSAGE, MessageRole
from services.assistant_service import get_assistant
from services.openai_client import get_client
from services.thread_service import get_thread, add_message, run_thread
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

    print()
    print("=" * 40)
    print(f"{Fore.CYAN}      TASK 1 Complete{Style.RESET_ALL}")
    print("=" * 40)
    print()


# Execution guard
if __name__ == "__main__":
    main()
