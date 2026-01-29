from typing import Optional, Any

import time
import requests
from openai.pagination import SyncCursorPage
from openai.types.beta import Thread
from openai.types.beta.threads import Run, Message
from datetime import datetime
from assistants import assistants

from config import Config
import json
from openai import OpenAI


available_time_series = [
    "TIME_SERIES_INTRADAY",
    "TIME_SERIES_DAILY",
    "TIME_SERIES_WEEKLY",
    "TIME_SERIES_MONTHLY"
]

client = OpenAI(api_key=Config.api_key, base_url=Config.base_url)

functions_list = [
    {
        "type": "function",
        "function": {
            "name": "retrieve_stock_data",
            "description": "When stock data is requested, Alpha Vantage will be used to retrieve stock data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "stock_symbol": {
                        "type": "string",
                        "description": "The stock symbol where stock data is desired"
                    },
                    "time_series": {
                        "type": "string",
                        "description": "One of possible time_series: TIME_SERIES_INTRADAY, TIME_SERIES_DAILY, TIME_SERIES_WEEKLY, TIME_SERIES_MONTHLY"
                    },
                    "interval": {
                        "type": "string",
                        "description": "One of possible intervals: 1min, 5min, 15min, 30min, 60min and is only available and required for time_series TIME_SERIES_INTRADAY"
                    },
                },
                "required": ["stock_symbol", "time_series"],
                "additionalProperties": False
            },
        }
    },
    {"type": "code_interpreter"}
]

def _expected_time_series_key(time_series: str) -> str:
    mapping = {
        "TIME_SERIES_INTRADAY": "Time Series (",
        "TIME_SERIES_DAILY": "Time Series (Daily)",
        "TIME_SERIES_WEEKLY": "Weekly Time Series",
        "TIME_SERIES_MONTHLY": "Monthly Time Series",
    }
    return mapping.get(time_series, "")

def retrieve_stock_data(stock_symbol: str, time_series: str, interval: str = None, use_cache: bool = False) -> Any:
    if use_cache:
        print("===> Using cached data for stock symbol:", stock_symbol)
        with open(f"alphavantage_AAPL_{time_series}.json", "r", encoding="utf-8") as f:
            return json.load(f)

    if time_series == "TIME_SERIES_INTRADAY" and not interval:
        interval = "30min"

    # replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
    # url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&apikey=demo'
    alpha_key = Config.alphavantage_key

    if time_series not in available_time_series:
        raise ValueError(f"Invalid time_series '{time_series}'. Expected one of: {available_time_series}")

    if time_series == "TIME_SERIES_INTRADAY" and not interval:
        raise ValueError("interval is required for TIME_SERIES_INTRADAY")

    if interval:
        url = (
            f"https://www.alphavantage.co/query?"
            f"function={time_series}&symbol={stock_symbol}&interval={interval}&apikey={alpha_key}"
        )
    else:
        url = f"https://www.alphavantage.co/query?function={time_series}&symbol={stock_symbol}&apikey={alpha_key}"

    r = requests.get(url, timeout=30)
    r.raise_for_status()
    data = r.json()

    if "Error Message" in data:
        raise RuntimeError(f"AlphaVantage error: {data['Error Message']}")
    if "Note" in data:
        raise RuntimeError(f"AlphaVantage rate-limit note: {data['Note']}")

    expected_key = _expected_time_series_key(time_series)
    if time_series == "TIME_SERIES_INTRADAY":
        # Intraday has dynamic key like "Time Series (5min)"
        if not any(k.startswith(expected_key) for k in data.keys()):
            raise RuntimeError(f"Unexpected response keys: {list(data.keys())}")
    else:
        if expected_key and expected_key not in data:
            raise RuntimeError(f"Unexpected response keys: {list(data.keys())}")

    # +++ for testing purposes only - save response to file +++
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"alphavantage_{stock_symbol}_{time_series}_{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Response saved in {filename}")
    # +++ end for testing purposes only +++

    return data

def load_cached_response(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _parse_tool_args(call) -> dict:
    try:
        args = json.loads(call.function.arguments or "{}")
        if not isinstance(args, dict):
            raise ValueError("Tool arguments must be a JSON object.")
        return args
    except json.JSONDecodeError as e:
        raise ValueError(f"Tool arguments were not valid JSON: {e}") from e

def handle_requires_action(openai_client:OpenAI, run: Run) -> Run:
    tool_calls = run.required_action.submit_tool_outputs.tool_calls
    tool_outputs = []
    print(f"required_action: {run.required_action.type}")
    for call in tool_calls:
        args = json.loads(call.function.arguments)

        if call.function.name == "retrieve_stock_data":
            print(f"Tool call with ID and name: {call.id} {call.function.name}")
            stock_symbol = args.get('stock_symbol') or args.get('symbol')
            time_series = args.get('time_series') or args.get('function')
            interval = args.get('interval')

            if not stock_symbol or not time_series:
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": json.dumps({
                        "error": "Missing required arguments for retrieve_stock_data.",
                        "received_arguments": args,
                        "required": ["stock_symbol", "time_series"],
                        "hint": "Provide JSON like: {\"stock_symbol\":\"AAPL\",\"time_series\":\"TIME_SERIES_DAILY\"}"
                    })
                })
                continue

            try:
                result = retrieve_stock_data(stock_symbol, time_series, interval, use_cache=True)
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": json.dumps(result)
                })
            except Exception as e:
                print(f"Error running retrieve_stock_data: {e}")
                tool_outputs.append({
                    "tool_call_id": call.id,
                    "output": json.dumps({"error": str(e)})
                })

        else:
            print(f"Unknown tool: {call.function.name}")
            tool_outputs.append({
                "tool_call_id": call.id,
                "output": json.dumps({"error": f"Unknown tool: {call.function.name}"})
            })
    # for every iteration, the output will be added to submit_tool_outputs to the same thread
    run = openai_client.beta.threads.runs.submit_tool_outputs(
        thread_id=run.thread_id,
        run_id=run.id,
        tool_outputs=tool_outputs
    )

    return run

# program flow
def execute(openai_client: OpenAI):
    start = time.perf_counter()

    assistant = assistants.create_assistant(openai_client, functions_list)

    # create thread for conversation
    thread = openai_client.beta.threads.create()
    print(f"Thread created with ID: {thread.id}")

    # add message to thread ==> includes the prompt
    openai_client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="Retrieve and visualize the monthly time series data for the stock symbol 'AAPL' for the latest 3 months."
        # content="Retrieve AAPL monthly time series for the latest 3 months. Use Python with matplotlib to create a chart of closing prices. Save the plot as 'stock-image
        # .png' and attach the image file to the assistant response. Do not return a markdown image reference."
    )
    # print(f"Message added to thread: {message.id}")

    # run assistant in thread
    run = openai_client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )
    print(f"Run initiated with ID: {run.id}")

    ############## stop time ########################################
    elapsed = time.perf_counter() - start
    print(
        f"Waiting for response from `{assistant.name}` Assistant. "
        f"Elapsed time: {elapsed:.2f} seconds"
    )
    #################################################################

    start_response = time.perf_counter()

    # Wait for the run to complete
    run = continuous_status_monitoring(openai_client, run, thread)

    elapsed_response = time.perf_counter() - start_response
    print(f"Done! Response received in {elapsed_response:.2f} seconds.")
    print()
    print(f"Run initiated with ID: {run.id}")

    # Retrieve the messages from the thread
    messages = openai_client.beta.threads.messages.list(
        thread_id=thread.id
    )

    # at this stage, the image should be available
    # is image there?
    # status = run.status
    # print(f"Run status: {status}") ==> is completed
    image_id = check_for_image_and_return_id(messages)
    if image_id:
        image_data = openai_client.files.content(image_id)
        image_data_bytes = image_data.read()
        with open("images/stock-image.png", "wb") as f:
            f.write(image_data_bytes)

    ##  Display the assistant's response
    # for message in messages.data:
    #     if message.role == "assistant":
    #         print(f"Assistant response: {message.content[0].text.value}")
    # ==> causes exception: AttributeError: 'ImageFileContentBlock' object has no attribute 'text'


    print_run_steps(openai_client, run, thread)


def continuous_status_monitoring(openai_client: OpenAI, run: Run, thread: Thread) -> Run:
    while run.status in {"queued", "in_progress", "requires_action"}:
        time.sleep(1)
        run = openai_client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )

        if run.status == "requires_action":
            run = handle_requires_action(openai_client, run)
            continue

    return run


def check_for_image_and_return_id(messages: SyncCursorPage[Message]) -> str | None:
    for msg in messages.data:
        if msg.role == "assistant":
            for item in msg.content:
                if item.type == "image_file":
                    image_file_id = item.image_file.file_id
                    # print("Image created(assistant):", image_file_id)
                    return image_file_id
    return None


def print_run_steps(openai_client: OpenAI, run: Run, thread: Thread):
    run_steps = openai_client.beta.threads.runs.steps.list(
        thread_id=thread.id,
        run_id=run.id
    )
    print()
    for step in run_steps.data:
        print(f"Step: {step.id}")
        # print(json.dumps(step.model_dump(), indent=2))


# start
execute(client)

