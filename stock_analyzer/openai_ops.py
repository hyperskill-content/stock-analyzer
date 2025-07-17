import json
import time
from pprint import pprint

import openai

from .alpha_vantage import functions_list, name_to_function
from .config import OPENAI_API_KEY, BASE_URL


def create_client():
    return openai.OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=BASE_URL
    )


def get_assistant(client):
    assistants_list = client.beta.assistants.list()
    for a in assistants_list.data:
        if a.name == "stock_analyzer_assistant":
            print(
                f"Matching `stock_analyzer_assistant` assistant found, using the first matching assistant with ID: {a.id}")
            return a

    new_assistant = client.beta.assistants.create(
        instructions="You're an experienced stock analyzer assistant tasked with analyzing and visualizing stock market data.",
        name="stock_analyzer_assistant",
        model="gpt-4o-mini",
        tools=functions_list
    )
    print(
        f"No matching `stock_analyzer_assistant` assistant found, creating a new assistant with ID: {new_assistant.id}")
    return new_assistant


def create_thread(client):
    thread = client.beta.threads.create()
    print(f"Thread created with ID: {thread.id}")
    return thread


def send_message_to_thread(client, thread, text):
    user_message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=text
    )
    print(f"Message added to thread: {user_message.id}")
    print(f"User message: {user_message.content[0].text.value}")


def execute_thread_run(client, assistant, thread):
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )
    print(f"Run initiated with ID: {run.id}")
    run = wait_for_run_completion(client, thread, run)
    pprint(run.required_action.to_dict(), indent=2, width=90, compact=False)
    if run.status == "requires_action":
        function_outputs = call_functions(run)
        run = client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=function_outputs
        )
        run = wait_for_run_completion(client, thread, run)


def wait_for_run_completion(client, thread, run):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        print(f"Run status: {run.status}")
        time.sleep(1)
    return run


def call_functions(run):
    function_outputs = []
    for tool_call in run.required_action.submit_tool_outputs.tool_calls:
        print(f"Tool call ID: {tool_call.id}")
        print(f"\tTool call function: {tool_call.function.name}")
        print(f"\tTool call function arguments: {tool_call.function.arguments}")
        action = name_to_function(tool_call.function.name)
        if action is not None:
            params = json.loads(tool_call.function.arguments)
            output = action(params)
            function_outputs.append({"tool_call_id": tool_call.id, "output": output})
    return function_outputs


def print_assistant_response(client, thread):
    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )
    for message in messages.data:
        if message.role == "assistant":
            print(f"Assistant: {message.content[0].text.value}")


def delete_assistants(client=None):
    if client is None:
        client = create_client()
    assistants_list = client.beta.assistants.list()
    for a in assistants_list.data:
        assistant_deleted = client.beta.assistants.delete(a.id)
        print(f"Assistant deleted: {assistant_deleted}")


def execute_full_conversation():
    client = create_client()
    assistant = get_assistant(client)
    thread = create_thread(client)
    send_message_to_thread(client, thread,
                           "Retrieve and show the latest daily time series data for the stock symbol 'AAPL'.")
    execute_thread_run(client, assistant, thread)
    print_assistant_response(client, thread)
