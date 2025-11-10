import os
import openai
import helpers
import requests
import time
import json

### Setup
api_key = os.getenv("OPENAI_API_KEY")
alpha_vantage_api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
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

# 1. Integrate Code Interpreter Tool
stock_analyzer_assistant = helpers.create_assistant(
    name=STOCK_ANALYZER_ASSISTANT_ID,
    instructions=STOCK_ANALYZER_ASSISTANT_INSTRUCTIONS,
    client=client,
    tools=tools
)

def get_stock_time_series(symbol, time_series_type = "TIME_SERIES_DAILY"):
    url = f"https://www.alphavantage.co/query?function={time_series_type}&symbol={symbol}&apikey={alpha_vantage_api_key}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

thread = client.beta.threads.create()

# 2. Prompt the Assistant
client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Retrieve the monthly time series data for the stock symbol 'AAPL' for the latest 3 months AND analyze the "
            "retrieved stock data and identify any trends, calculate ratios, key metrics, etc."
)

run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=stock_analyzer_assistant.id
)

while True:
    time.sleep(5)
    run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    if run.status == "completed":
        break
    elif run.status == "requires_action":
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        tool_outputs = []
        for tool_call in tool_calls:
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
        print(f"Assistant response: {message.content[0].text.value}")

# 3. Print the Steps
run_steps = client.beta.threads.runs.steps.list(
    thread_id=thread.id,
    run_id=run.id
)
for step in run_steps.data:
    print(f"Step: {step.id}")
