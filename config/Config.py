import os

from dotenv import load_dotenv

load_dotenv()


api_key=os.environ.get("OPENAI_API_KEY", None)
base_url=os.environ.get("BASE_URL", None)

assistant_name = "stock_analyzer_assistant"
assistant_instruction = (
    "You're an experienced stock analyzer assistant tasked with analyzing and visualizing stock market data. "
    "You can use Code Interpreter for generating plots and visualizations based on stock data."
)
assistant_model = "gpt-4o-mini"

alphavantage_key = os.environ.get("ALPHAVANTAGE_API_KEY", None)

user_prompt = "Retrieve and visualize the monthly time series data for the stock symbol 'AAPL' for the latest 3 months."

