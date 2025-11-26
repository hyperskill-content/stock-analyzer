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

##############
### TASK 1 ###
##############
### 1. Set Up the Assistant
stock_analyzer_assistant = helpers.create_assistant(
    name=STOCK_ANALYZER_ASSISTANT_ID,
    instructions=STOCK_ANALYZER_ASSISTANT_INSTRUCTIONS,
    client=client
)

### 2. Validate Assistant Existence
# done inside the create_assistant function in step 1

### 3. Create a Thread Object
thread = client.beta.threads.create()
print(f"Thread created with ID: {thread.id}")


### 4. Send a Message to the Thread
client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Tell me your name and instructions. YOU MUST Provide a DIRECT and SHORT response."
)

### 5. Execute a Run Instance
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=stock_analyzer_assistant.id,
)
print(f"Run initiated with ID: {run.id}")

while run.status != "completed":
    time.sleep(3)
    run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

##############
### TASK 2 ###
##############
### 1. Set Up the Stock API
def get_stock_time_series(symbol, time_series_type = "TIME_SERIES_DAILY"):
    # It's the API Endpoint from the provider
    url = f"https://www.alphavantage.co/query?function={time_series_type}&symbol={symbol}&apikey={alpha_vantage_api_key}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


### 2. Define the Tools
tools = [
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
client.beta.assistants.update(
    assistant_id=stock_analyzer_assistant.id,
    tools=tools
)

### 3. Trigger the Action with a Prompt
client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Retrieve and show the latest daily time series data for the stock symbol 'AAPL'."
)
start_timestamp = time.time()
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=stock_analyzer_assistant.id
)

### 4. Handle the requires_action State
while True:
    time.sleep(3)
    run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    if run.status == "completed":
        break
    elif run.status == "requires_action":
        stop_timestamp = time.time()
        elapsed_time = stop_timestamp - start_timestamp
        print(f"Waiting for response from `{STOCK_ANALYZER_ASSISTANT_ID}` Assistant. Elapsed time: {elapsed_time}")
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        tool_outputs = []
        for tool_call in tool_calls:
            if tool_call.function.name == "get_stock_time_series":
                print(f"Tool call with ID and name: {tool_call.id} {tool_call.function.name}")
                args = json.loads(tool_call.function.arguments)
                start_timestamp = time.time()
                stock_data = get_stock_time_series(
                    symbol=args.get("symbol"),
                    time_series_type=args.get("time_series_type")
                )
                stop_timestamp = time.time()
                elapsed_time = stop_timestamp - start_timestamp
                print(f"Done! Response received in {elapsed_time} seconds.")
                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": json.dumps(stock_data)
                })
        client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=tool_outputs
        )
        print(f"Run initiated with ID: {run.id}")
    else:
        time.sleep(1)

messages = client.beta.threads.messages.list(thread_id=thread.id)
for message in reversed(messages.data):
    if message.role == "assistant":
        print(f"Assistant response: {message.content[0].text.value}")