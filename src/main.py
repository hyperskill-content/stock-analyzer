import json
import os
import time
import warnings
import requests
import dotenv
from openai import OpenAI

warnings.filterwarnings("ignore")
dotenv.load_dotenv()
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url=os.environ.get("BASE_URL")
)


def get_stock_data(stock):
    print(f"Fetching stock data for: {stock}")
    response = requests.get(os.environ.get("ALPHAVANTAGE_BASE_URL"), {
        "function": "TIME_SERIES_DAILY",
        "symbol": stock,
        "apikey": os.environ.get("ALPHAVANTAGE_API_KEY")
    })
    print("Stock Data Response:", response.json())
    return json.dumps(response.json())


functions_list = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_data",
            "description": "Get Stock Data",
            "parameters": {
                "type": "object",
                "properties": {
                    "s": {"type": "string",
                          "description": "The stock we need to fetch data for. A four letter abbreviation"}
                },
                "required": ["s"],
            },
        },
    },
    {
        "type": "code_interpreter",
    }
]

isCreated = False
stock_analyzer_assistant = None
for assistant in client.beta.assistants.list().data:
    if assistant.name == "stock_analyzer_assistant":
        isCreated = True
        stock_analyzer_assistant = client.beta.assistants.update(
            assistant_id=assistant.id,
            instructions="You are a stock market analysis assistant. Provide insights and analysis on stock market trends based on user queries.",
            model="gpt-4o-mini",
            name="stock_analyzer_assistant",
            tools=functions_list,
        )
        print("Matching `stock_analyzer_assistant` assistant found, using the first matching assistant with ID:",
              stock_analyzer_assistant.id)
        break
if not isCreated:
    stock_analyzer_assistant = client.beta.assistants.create(
        instructions="You are a stock market analysis assistant. Provide insights and analysis on stock market trends based on user queries.",
        model="gpt-4o-mini",
        name="stock_analyzer_assistant",
        tools=functions_list,
    )
    print("Matching `stock_analyzer_assistant` assistant not found, created with this ID:", stock_analyzer_assistant.id)
empty_thread = client.beta.threads.create()
print("Thread created with ID:", empty_thread.id)
thread_message = client.beta.threads.messages.create(
    empty_thread.id,
    role="user",
    content="Retrieve and visualize the monthly time series data for the stock symbol 'AAPL' for the latest 3 months."
)
run = client.beta.threads.runs.create(
    empty_thread.id,
    assistant_id=stock_analyzer_assistant.id
)

print("Run initiated with ID:", run.id)
tool_outputs = []
while run.status in ("queued", "in_progress"):
    time.sleep(1)
    run = client.beta.threads.runs.retrieve(thread_id=empty_thread.id, run_id=run.id)
    if run.status == "requires_action":
        start_time = time.perf_counter()
        tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        get_stock_data_response = get_stock_data(stock=function_args["s"])
        tool_outputs.append({
            "tool_call_id": tool_call.id,
            "output": get_stock_data_response
        })
        end_time = time.perf_counter()
        print(f"Tool call with ID and name: {tool_call.id} {function_name}")
        print(f"Done! Response received in {end_time - start_time:.2f} seconds.")

run = client.beta.threads.runs.submit_tool_outputs_and_poll(
    thread_id=empty_thread.id,
    run_id=run.id,
    tool_outputs=tool_outputs
)
file_id = None
if run.status == 'completed':
    messages = client.beta.threads.messages.list(
        thread_id=empty_thread.id
    )
    print("Messages")
    for message in messages.data:
        for content in message.content:
            if content.type == "text":
                print("Assistant text response:", content.text.value)
            elif content.type == "image_file":
                file_id = content.image_file.file_id

    print("Let's visualize this data to better understand the stock performance over the last 3 months.")
    print("assistant", file_id)
    run_steps = client.beta.threads.runs.steps.list(
        thread_id=empty_thread.id,
        run_id=run.id,
    )
    print("Run Steps:")
    for step in run_steps.data:
        print(f"Step: {step.id}")

    image_data = client.files.content(file_id)
    image_data_bytes = image_data.read()

    with open("./stock-perormance.png", "wb") as file:
        file.write(image_data_bytes)
