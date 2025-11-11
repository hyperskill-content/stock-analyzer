"""
Configuration settings for the Stock Analyzer application.

Handles loading and validation of environment variables from .env file.
Provides centralized access to configuration values.
"""

# Imports
import os
from dotenv import load_dotenv
from colorama import Fore, Style

# Load environment variables once when module is imported
load_dotenv()


class Settings:
    """Configuration settings container."""

    def __init__(self):
        """Initialize settings and validate required variables."""
        self._openai_api_key = os.environ.get('OPENAI_API_KEY')
        self._openai_base_url = os.environ.get('BASE_URL')
        self._alpha_vantage_api_key = os.environ.get('ALPHAVANTAGE_API_KEY')

        # Validate required settings
        self._validate()

    def _validate(self):
        """Validate that required environment variables are set."""
        missing = []

        if not self._openai_api_key:
            missing.append('OPENAI_API_KEY')
        if not self._alpha_vantage_api_key:
            missing.append('ALPHAVANTAGE_API_KEY')

        if missing:
            print(f"{Fore.RED}Error: Missing required environment variables:{Style.RESET_ALL}")
            for var in missing:
                print(f"  - {var}")
            print(f"\n{Fore.YELLOW}Please ensure these are set in your .env file{Style.RESET_ALL}")
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    @property
    def openai_api_key(self) -> str:
        """Get OpenAI API key."""
        return self._openai_api_key

    @property
    def openai_base_url(self) -> str:
        """Get OpenAI base URL."""
        return self._openai_base_url

    @property
    def alpha_vantage_api_key(self) -> str:
        """Get Alpha Vantage API key."""
        return self._alpha_vantage_api_key


# Create a singleton instance to be imported by other modules
settings = Settings()


def get_settings() -> Settings:
    """
    Get the application settings instance.

    :return: Settings instance with loaded configuration
    """
    return settings
