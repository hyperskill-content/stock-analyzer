import dotenv

# dotenv.load_dotenv()

OPENAI_API_KEY = dotenv.get_key(".env", "OPENAI_API_KEY")
BASE_URL = dotenv.get_key(".env", "BASE_URL")
ALPHAVANTAGE_API_KEY = dotenv.get_key(".env", "ALPHAVANTAGE_API_KEY")