import os
import openai
import helpers
import requests
import time
import json

### Setup
api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key, base_url="https://litellm.aks-hs-prod.int.hyperskill.org/openai")
STOCK_ANALYZER_ASSISTANT_ID = "stock_analyzer_assistant"
STOCK_ANALYZER_ASSISTANT_INSTRUCTIONS = "You're an experienced stock analyzer assistant tasked with analyzing and visualizing stock market data."
tools = [
    {"type": "code_interpreter"},
    {
        "type": "function",
        "function": {
            "name": "get_stock_time_series",
            "description": "Gets the requested time series for a stock symbol.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "The stock symbol to get data for."
                    },
                    "time_series_type": {
                        "type": "string",
                        "enum": ["TIME_SERIES_INTRADAY", "TIME_SERIES_DAILY", "TIME_SERIES_WEEKLY", "TIME_SERIES_MONTHLY"],
                        "description": "The type of time series to get."
                    }
                },
                "required": ["symbol"]
            }
        }
    }
]

stock_analyzer_assistant = helpers.create_assistant(
    name=STOCK_ANALYZER_ASSISTANT_ID,
    instructions=STOCK_ANALYZER_ASSISTANT_INSTRUCTIONS,
    client=client,
    tools=tools
)

def get_stock_time_series(symbol, time_series_type = "TIME_SERIES_DAILY"):
    """
    url = f"https://www.alphavantage.co/query?function={time_series_type}&symbol={symbol}&apikey=F5W6Z82V2EPL7TEA"

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"error {str(e)}")
    """
    return {
        "Meta Data": {
            "1. Information": "Monthly Prices (open, high, low, close) and Volumes",
            "2. Symbol": "AAPL",
            "3. Last Refreshed": "2024-03-11",
            "4. Time Zone": "US/Eastern"
        },
        "Monthly Time Series": {
            "2024-03-11": {
                "1. open": "185.4900",
                "2. high": "198.7300",
                "3. low": "185.1800",
                "4. close": "191.7300",
                "5. volume": "37816338"
            },
            "2024-02-29": {
                "1. open": "183.6300",
                "2. high": "188.9500",
                "3. low": "178.7500",
                "4. close": "185.0300",
                "5. volume": "88679550"
            },
            "2024-01-31": {
                "1. open": "162.8300",
                "2. high": "196.9000",
                "3. low": "157.8850",
                "4. close": "183.6600",
                "5. volume": "128121557"
            }
        }
    }


thread = client.beta.threads.create()

# 1. Write Prompt for Visuals
client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Retrieve the monthly time series data for the stock symbol 'AAPL' for the latest 3 months. Generate an image visualizing it."
)

run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=stock_analyzer_assistant.id
)

while True:
    time.sleep(10)
    run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    if run.status == "completed":
        break
    elif run.status == "requires_action":
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        tool_outputs = []
        for tool_call in tool_calls:
            print(tool_call)
            if tool_call.function.name == "get_stock_time_series":
                args = json.loads(tool_call.function.arguments)
                stock_data = get_stock_time_series(
                    symbol=args.get("symbol"),
                    time_series_type=args.get("time_series_type")
                )
                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": json.dumps(stock_data)
                })
        client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=tool_outputs
        )

messages = client.beta.threads.messages.list(thread_id=thread.id)
for message in messages.data:
    if message.role == "assistant":
        print(message)
        # 2. Handle Generated File
        for content in message.content:
            if hasattr(content, "text"):
                print(f"Assistant response: {content.text.value}")
            if hasattr(content, "type") and content.type == "image_file":
                file_id = content.image_file.file_id
                print(f"File Id: {file_id}")

                # Download the file content
                file_content = client.files.content(file_id)

                # Write a binary file as an image
                with open("images/stock-image.png", "wb") as f:
                    f.write(file_content.read())

time.sleep(3)
run_steps = client.beta.threads.runs.steps.list(
    thread_id=thread.id,
    run_id=run.id
)
for step in run_steps.data:
    print(f"Step: {step.id}")
