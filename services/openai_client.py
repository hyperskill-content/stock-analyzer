# Imports
from openai import OpenAI
from dotenv import load_dotenv
import os


# Functions
def get_openai_client():
    """
    Initialize and return the OpenAI client.
    Uses OPENAI_API_KEY and BASE_URL from environment variables.
    :return: Configured OpenAI client instance
    """
    load_dotenv()
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    openai_base_url = os.environ.get('BASE_URL')

    return OpenAI(
        api_key=openai_api_key,
        base_url=openai_base_url
    )
