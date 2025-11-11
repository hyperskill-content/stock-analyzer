"""
OpenAI client initialization service.

Handles the creation and configuration of the OpenAI client instance
with credentials from a centralized configuration.
"""

# Imports
from colorama import Fore, Style
from config.settings import settings
from openai import OpenAI


# Functions
def get_client():
    """
    Initialize and return the OpenAI client.
    Uses configuration from the settings module.
    :return: Configured OpenAI client instance
    """
    try:
        client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url
        )
        print(f"{Fore.GREEN}Created OpenAI client{Style.RESET_ALL}")
        return client
    except Exception as e:
        print(f"{Fore.RED}Error: Failed to initialize OpenAI client.{Style.RESET_ALL}")
        print(f"Details: {e}")
        exit(1)
