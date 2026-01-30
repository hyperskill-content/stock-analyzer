from dotenv import load_dotenv
from openai import OpenAI
import os
import time
import requests
import json
import warnings

warnings.filterwarnings('ignore', category=DeprecationWarning)
load_dotenv()
ASSISTANT_NAME = "stock_analyzer_assistant2"
URL_ALPHAVANTAGE = "https://www.alphavantage.co/query"

try:
    client = OpenAI(api_key = os.environ['OPENAI_API_KEY'])
    API_KEY_ALPHAVANTAGE = os.environ['ALPHAVANTAGE_API_KEY']
except KeyError as e:
    print(f"Error: Environment variable {e} not found!")

def validate_assistant():
    assistants = client.beta.assistants.list()
    for assistant in assistants.data:
        if assistant.name == ASSISTANT_NAME:
            return assistant.id
    return None

def upload_file(file_path, purpose):
    existing_id = validate_existing_file_id("sample_visual.jpg")
    if existing_id:
        print(f"File found! ID: {existing_id}")
    else:
        with open(file_path, "rb") as file:
            uploaded_file = client.files.create(
                file=file,
                purpose=purpose
            )
            existing_id = uploaded_file.id
    return existing_id


def validate_existing_file_id(target_filename, purpose="vision"):
    # List all files for your project
    files = client.files.list()

    # Iterate through the list to find a match
    for file in files.data:
        if file.filename == target_filename and file.purpose == purpose:
            return file.id
    return None

def create_assistant():
    tools = [
        {"type": "code_interpreter"},
        {
            "type": "function",
            "function": {
                "name": "get_company_symbol",
                "description": "Look the specific company's symbol base in the company's name.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keyword": {"type": "string", "description": "The company's name keyword."}
                    },
                    "required": ["keyword"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_frequency_function",
                "description": "Get the name of the frequency function based on the given keyword, the keyword must be daily, interdaily, weekly, monthly.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keyword": {"type": "string", "description": "The frequency keyword."}
                    },
                    "required": ["keyword"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_stock_data",
                "description": "Get the specific data of the stock based on the company symbol and the name frequency function.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "company_symbol": {"type": "string", "description": "The company symbol."},
                        "frequency_function": {"type": "string", "description": "The frequency function."}
                    },
                    "required": ["company_symbol", "frequency_function"]
                }
            }
        }
    ]
    assistant = client.beta.assistants.create(
        name=ASSISTANT_NAME,
        instructions="You're an experienced stock analyzer assistant tasked with analyzing and visualizing stock market data.",
        model="gpt-4o-mini",
        tools=tools
    )
    return assistant.id

def create_thread_message(message_content, file_id=None):
    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=[
            {
                "type": "text",
                "text": message_content
            },
            {
                "type": "image_file",
                "image_file": {"file_id": file_id}
            }
        ],
    )
    return thread.id

def run_thread(assistant_id, thread_id):
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
    )
    return run.id

def get_company_symbol(keyword):
    params = {
        'function': 'SYMBOL_SEARCH',
        'keywords': keyword,
        'apikey': API_KEY_ALPHAVANTAGE
    }
    response = requests.get(URL_ALPHAVANTAGE, params=params)
    data = response.json()
    if "bestMatches" in data and len(data["bestMatches"]) > 0:
        return data["bestMatches"][0]["1. symbol"]
    else:
        raise ValueError("Company symbol not found for the given keyword.")

def get_frequency_function(keyword):
    frequency_map = {
        "daily": "TIME_SERIES_DAILY",
        "interdaily": "TIME_SERIES_INTRADAY",
        "weekly": "TIME_SERIES_WEEKLY",
        "monthly": "TIME_SERIES_MONTHLY"
    }
    return frequency_map.get(keyword.lower(), "Invalid frequency keyword.")

def get_stock_data(company_symbol, frequency_function):
    params = {
        'function': frequency_function,
        'symbol': company_symbol,
        'apikey': API_KEY_ALPHAVANTAGE
    }
    response = requests.get(URL_ALPHAVANTAGE, params=params)
    data = response.json()
    if "Meta Data" in data:
        return data #data = get_mock_stock(company_symbol) Test with mock data
    else:
        raise ValueError("Stock data not found for the given symbol and frequency function.")

def get_mock_stock(stock_symbol):
    mock_data = {
        "Meta Data": {
            "1. Information": "Monthly Prices (open, high, low, close) and Volumes",
            "2. Symbol": "IBM",
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
    return mock_data

def get_response(thread_id, run_id):
    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        if run.status == "completed":
            break
        elif run.status == "requires_action":
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            tool_outputs = []
            for tool_call in tool_calls:
                print( f"Tool call with ID and name: {tool_call.id} {tool_call.function.name}" )
                # Extract the function name and the arguments
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                data = None
                if function_name == "get_company_symbol":
                    data = get_company_symbol(
                        keyword=function_args.get("keyword"),
                    )
                    print("Company Symbol:", data)
                if function_name == "get_frequency_function":
                    data = get_frequency_function(
                        keyword=function_args.get("keyword"),
                    )
                    print("Frequency function", data)
                if function_name == "get_stock_data":
                    data = get_stock_data(
                        company_symbol=function_args.get("company_symbol"),
                        frequency_function=function_args.get("frequency_function"),
                    )
                    #print("Symbol and Frequency function", data)
                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": json.dumps(data)
                })

            client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )
        else:
            time.sleep(1)
    messages = client.beta.threads.messages.list(thread_id)
    for message in messages.data:
        if message.role == "assistant":
            return message.content
    return None

def view_steps(thread_id, run_id):
    steps = client.beta.threads.runs.steps.list(thread_id=thread_id, run_id=run_id)
    for step in steps.data:
        print(f"Step ID: {step.id}")

def main():
    prompt = '''1. Retrieve the IBM stock’s monthly price data (e.g., open, high, low, close, and volume) for the latest three months.
                2. Show the retrieved data clearly as formatted text for each month.
                3. Create a visualization inspired by the provided reference image'''
    start_time = time.perf_counter()
    assistant_id = validate_assistant()

    if assistant_id:
        print(f"No matching `{ASSISTANT_NAME}` assistant found, creating a new assistant with ID: {assistant_id}")
    else:
        assistant_id = create_assistant()
        print(f"Matching `{ASSISTANT_NAME}` assistant found, using the first matching assistant with ID: {assistant_id}")

    file_id = upload_file("images/sample_visual.jpg", purpose="vision")
    thread_id = create_thread_message(prompt, file_id)
    print(f"Thread created with ID: {thread_id}")

    run_id = run_thread(assistant_id,thread_id)
    print(f"Run initiated with ID: {run_id}")

    elapsed_time = time.perf_counter() - start_time
    print(f"Waiting for response from `{ASSISTANT_NAME}` Assistant. Elapsed time: {elapsed_time:.2f} seconds")
    assistant_response = get_response(thread_id, run_id)
    end_time = time.perf_counter()
    print(f"Done! Response received in {end_time - start_time:.2f} seconds")

    for content in assistant_response:
        if content.type == "image_file":
            file_id = content.image_file.file_id
            file_data = client.files.content(file_id)
            with open("stock-image.png", "wb") as f:
                f.write(file_data.read())
        elif content.type == "text":
            print(f"Assistant Response: {content.text.value}")
    view_steps(thread_id, run_id)

if __name__ == "__main__":
    main()
