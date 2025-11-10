"""
OpenAI client initialization service.

Handles the creation and configuration of the OpenAI client instance
with credentials from environment variables.
"""

# Imports
from colorama import Fore, Style
from dotenv import load_dotenv
from openai import OpenAI
import os


# Functions
def get_client():
    """
    Initialize and return the OpenAI client.
    Uses OPENAI_API_KEY and BASE_URL from environment variables.
    :return: Configured OpenAI client instance
    """
    load_dotenv()
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    openai_base_url = os.environ.get('BASE_URL')

    try:
        client = OpenAI(
            api_key=openai_api_key,
            base_url=openai_base_url
        )
        print(f"{Fore.GREEN}Created OpenAI client{Style.RESET_ALL}")
        return client
    except Exception as e:
        print(f"{Fore.RED}Error: Failed to initialize OpenAI client.{Style.RESET_ALL}")
        print(f"Details: {e}")
        exit(1)
