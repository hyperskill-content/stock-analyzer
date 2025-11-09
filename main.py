import os
from openai import OpenAI
from dotenv import load_dotenv
import requests
import json
import time


def create_client():
    load_dotenv()

    # Retrieve the OpenAI API key from environment variables
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    base_url = os.getenv("BASE_URL")
    if not base_url:
        raise ValueError("OPENAI_API_URL not found in environment variables")

    # Initialize the OpenAI client with the API key and base URL
    client = OpenAI(api_key=api_key, base_url=base_url)
    return client

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_data",
            "description": "Get time series stock data for a certain stock .",
            "parameters": {
                "type": "object",
                "properties": {
                    "function": {"type": "string",
                                 "enum": ["TIME_SERIES_INTRADAY", "TIME_SERIES_DAILY", "TIME_SERIES_WEEKLY",
                                          "TIME_SERIES_MONTHLY"]},
                    "symbol": {"type": "string"}
                },
                "required": ["function", "symbol"]
            }
        }
    }
]

def start_assistant(client, content: str):

    assistant_name = "stock_analyzer_assistant"

    list_assistants = client.beta.assistants.list().data
    assistant_id = None

    for assistant in list_assistants:
        if assistant.name == assistant_name:
            assistant_id = assistant.id
            print(f"Matching `{assistant_name}` assistant found, using the first matching assistant with ID: {assistant.id}")
            break

    if not assistant_id:
        assistant = client.beta.assistants.create(
            name=assistant_name,
            instructions="You're an experienced stock analyzer assistant tasked with analyzing and visualizing stock market data.",
            model="gpt-4"
        )
        print(f"No matching `{assistant_name}` assistant found, creating a new assistant with ID: {assistant.id}")
        assistant_id = assistant.id

    client.beta.assistants.update(
        assistant_id=assistant_id,
        tools=tools
    )

    stock_api_key = os.getenv("STOCK_API_KEY")
    if not stock_api_key:
        raise ValueError("STOCK_API_KEY not found in environment variables")

    stock_api_url = os.getenv("STOCK_API_URL")
    if not stock_api_url:
        raise ValueError("STOCK_API_URL not found in environment variables")

    thread = client.beta.threads.create()
    print(f"Thread created with ID: {thread.id}")

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=content
    )

    start_time = time.time()
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id
    )

    print(f"Run initiated with ID: {run.id}")

    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if run.status == "completed":
            stop_timestamp = time.time()
            elapsed_time = stop_timestamp - start_time
            print(f"Done! Response received in {elapsed_time} seconds.")
            break
        elif run.status == "requires_action":
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            tool_outputs = []
            for tool_call in tool_calls:
                if tool_call.function.name == "get_stock_data":
                    stop_timestamp = time.time()
                    elapsed_time = stop_timestamp - start_time
                    print(f"Waiting for response from stock_analyzer_assistant Assistant. Elapsed time: {elapsed_time}")
                    args = json.loads(tool_call.function.arguments)
                    print(f"Tool call with ID: {tool_call.id} and name : {tool_call.function.name}")
                    stock_data = get_stock_data(
                        url=stock_api_url,
                        function=args.get("function"),
                        symbol=args.get("symbol"),
                        api_key=stock_api_key
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
        else:
            time.sleep(3)

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    for message in messages.data:
        if message.role == "assistant":
            print(f"Assistant: {message.content[0].text.value}")


def get_stock_data(url, function, symbol, api_key):
    params = {
        "function": function,
        "symbol": symbol,
        "apikey": api_key
    }
    response = requests.get(url, params)
    data = response.json()
    return data


def delete_assistant(client, assistant_id):
    if client is not None:
        assistants_list = client.beta.assistants.list()
        for assistant in assistants_list.data:
            if assistant.id == assistant_id:
                client.beta.assistants.delete(assistant.id)
                print(f"Assistant deleted: {assistant}")
                break

if __name__ == "__main__":
    llm_client = create_client()
    start_assistant(llm_client, "Retrieve and show the latest daily time series data for the stock symbol 'AAPL'")
