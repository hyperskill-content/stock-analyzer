import datetime
import json
import os
import time
import warnings

import pandas as pd
import requests
from dotenv import load_dotenv
from openai import OpenAI


def get_today() -> datetime.datetime:
    """
    Retrieves the current date and time.

    This function returns the current date and time as a `datetime` object,
    representing the system's local time when the function is called.

    :return: The current date and time.
    :rtype: datetime.datetime
    """
    return datetime.datetime.today()


def get_stock_data(
        symbol: str,
        function: str,
        interval: str,
        start_date: str | pd.Timestamp | None,
        end_date: str | pd.Timestamp | None,
) -> pd.DataFrame:
    """
    Retrieve and process stock data from Alpha Vantage API.
    Parameters:
    -----------
    symbol : str
        Stock symbol (e.g., 'AAPL' for Apple Inc.).
    function : str
        The time series function to use. Options include:
        - "TIME_SERIES_INTRADAY"
        - "TIME_SERIES_DAILY"
        - "TIME_SERIES_WEEKLY"
        - "TIME_SERIES_MONTHLY"
    interval : str
        Time interval between data points, only used with "TIME_SERIES_INTRADAY".
        Valid values: '1min', '5min', '15min', '30min', '60min'.
    start_date : str or datetime or None
        The start date for filtering the data. If None, no start filter is applied.
    end_date : str or datetime or None
        The end date for filtering the data. If None, no end filter is applied.
    Returns:
    --------
    pandas.DataFrame
        A DataFrame containing the processed stock data with columns:
        - open: Opening price
        - high: Highest price
        - low: Lowest price
        - close: Closing price
        - volume: Trading volume
        The DataFrame is indexed by datetime and sorted chronologically.
    Notes:
    ------
    This function requires the ALPHA_VANTAGE_API_KEY environment variable to be set.
    The API key can be obtained from https://www.alphavantage.co/support/#api-key.
    """
    alpha_vantage_api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    url = f"https://www.alphavantage.co/query"
    params = {
        "function": function,
        "symbol": symbol,
        "outputsize": "full",
        "apikey": alpha_vantage_api_key,
    }
    if function == "TIME_SERIES_INTRADAY":
        params["interval"] = interval
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()
    last_key = next(reversed(data.keys()))
    ohlcv = data[last_key]
    df = pd.DataFrame.from_dict(ohlcv, orient="index")
    df = df.astype(float)
    df = df.rename(
        columns={
            "1. open": "open",
            "2. high": "high",
            "3. low": "low",
            "4. close": "close",
            "5. volume": "volume",
        }
    )
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    if start_date is not None and end_date is not None:
        df = df[(df.index >= start_date) & (df.index <= end_date)]
    elif start_date is not None:
        df = df[df.index >= start_date]
    elif end_date is not None:
        df = df[df.index <= end_date]

    return df


def main():
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("BASE_URL")
    client = OpenAI(
        api_key=openai_api_key,
        base_url=base_url
    )

    warnings.filterwarnings("ignore", category=DeprecationWarning)

    existing_assistants = client.beta.assistants.list()
    assistant_name = "stock_analyzer_assistant"
    assistant = next((assistant for assistant in existing_assistants.data if assistant.name == assistant_name), None)

    if assistant:
        print(
            f"Matching `{assistant_name}` assistant found, using the first matching assistant with ID: {assistant.id}")
    else:
        description = """
            Retrieve and process stock data from Alpha Vantage API. 
            If the user requests latest daily time series set start_date yesterday and end_date yesterday. 
            If the user makes no mention to a date interval default to end_date None and start_date 3 days ago. 
        """
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_stock_data",
                    "description": description,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "Stock symbol (e.g., 'AAPL' for Apple Inc.).",
                            },
                            "function": {
                                "type": "string",
                                "enum": ["TIME_SERIES_INTRADAY", "TIME_SERIES_DAILY", "TIME_SERIES_WEEKLY",
                                         "TIME_SERIES_MONTHLY"],
                                "description": "Time frame of data: intraday, daily, weekly, monthly",
                            },
                            "interval": {
                                "type": "string",
                                "enum": ["1min", "5min", "15min", "30min", "60min"],
                                "description": "Intraday interval in minutes. Required only when function is TIME_SERIES_INTRADAY",
                            },
                            "start_date": {
                                "type": "string",
                                "description": "The start date for filtering the data (format: YYYY-MM-DD or datetime). If None, no start filter is applied.",
                            },
                            "end_date": {
                                "type": "string",
                                "description": "The end date for filtering the data (format: YYYY-MM-DD or datetime). If None, no end filter is applied.",
                            }
                        },
                        "required": ["symbol", "function"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_today",
                    "description": "Retrieves the current date and time as a datetime object.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "code_interpreter"
            }
        ]
        assistant = client.beta.assistants.create(
            name="stock_analyzer_assistant",
            instructions="You're an experienced stock analyzer assistant tasked with analyzing and visualizing stock market data.",
            model="gpt-4o-mini",
            tools=tools,
        )
        print(f"No matching `{assistant_name}` assistant found, creating a new assistant with ID: {assistant.id}")
    assistant_id = assistant.id

    thread = client.beta.threads.create()
    thread_id = thread.id
    print(f"Thread created with ID: {thread_id}")

    prompt = """Retrieve the monthly time series data for the stock symbol 'AAPL' for the latest 3 months.
    Analyze the retrieved stock data and identify any trends, calculate ratios, key metrics, etc.
    """
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=prompt
    )

    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    print(f"Run initiated with ID: {run.id}")

    start_time = time.time()
    run = client.beta.threads.runs.poll(
        run_id=run.id,
        thread_id=thread.id
    )
    elapsed_time = time.time() - start_time
    print(f"Waiting for response from `{assistant_name}` Assistant. Elapsed time: {elapsed_time:.2f} seconds")

    while run.status == "requires_action":
        tool_outputs = []

        for tool in run.required_action.submit_tool_outputs.tool_calls:
            tool_id = tool.id
            function_name = tool.function.name
            output_str = None

            print(f"Tool call with ID and name:  {tool_id} {function_name}")

            if function_name == "get_today":
                start_time = time.time()
                data = get_today()
                output_str = data.strftime("%Y-%m-%d")
                elapsed_time = time.time() - start_time
                print(f"Done! Response received in {elapsed_time:.2f} seconds.")

            elif tool.function.name == "get_stock_data":
                start_time = time.time()
                arguments = json.loads(tool.function.arguments)
                symbol = arguments.get("symbol")
                function = arguments.get("function")
                interval = arguments.get("interval")
                start_date = arguments.get("start_date")
                end_date = arguments.get("end_date")
                data = get_stock_data(symbol, function, interval, start_date, end_date)
                output_str = data.to_string()
                elapsed_time = time.time() - start_time
                print(f"Done! Response received in {elapsed_time:.2f} seconds.")

            if output_str is not None:
                tool_outputs.append({
                    "tool_call_id": tool.id,
                    "output": output_str
                })

        run = client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=tool_outputs
        )
        print(f"Run initiated with ID: {run.id}")

        run = client.beta.threads.runs.poll(
            run_id=run.id,
            thread_id=thread.id
        )

    if run.status == "completed":
        print("\n# Messages")
        messages = client.beta.threads.messages.list(
            thread_id=thread.id,
        )
        for message in reversed(messages.data):
            author = "assistant" if message.assistant_id is not None else "user"
            for content in reversed(message.content):
                if content.type == "text":
                    print(f"{author}: {content.text.value.replace("**", "")}")

        print()
        steps = client.beta.threads.runs.steps.list(
            thread_id=thread.id,
            run_id=run.id
        )
        for step in steps:
            print(f"Step: {step.id}")

    else:
        print(run.status)


if __name__ == "__main__":
    main()
