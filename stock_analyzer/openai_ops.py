import json
import time
from pprint import pprint

import openai
from openai.types.beta.threads.runs import ToolCallsStepDetails
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import PythonLexer

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

    tools = functions_list + [{"type": "code_interpreter"}]
    new_assistant = client.beta.assistants.create(
        instructions="You're an experienced stock analyzer assistant tasked with analyzing and visualizing stock market data.",
        name="stock_analyzer_assistant",
        model="gpt-4o-mini",
        tools=tools,
    )
    print(
        f"No matching `stock_analyzer_assistant` assistant found, creating a new assistant with ID: {new_assistant.id}")
    return new_assistant


def create_thread(client: openai.OpenAI):
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
    if run.status == "requires_action":
        function_outputs = call_functions(run)
        run = client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=function_outputs
        )
        run = wait_for_run_completion(client, thread, run)
    return run


def wait_for_run_completion(client, thread, run):
    print(f"Waiting for run {run.id} completion...", end="")
    start = time.perf_counter()
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        time.sleep(1)
    end = time.perf_counter()
    print(f"\rRun {run.id} completed in {end - start:.2f} seconds  ")
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


def print_assistant_response(client: openai.OpenAI, thread):
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    for message in messages.data:
        if message.role == "assistant":
            for content_block in message.content:
                if content_block.type == 'text':
                    print(f"Assistant: {content_block.text.value}")
                elif content_block.type == 'image_file':
                    file_id = content_block.image_file.file_id
                    print(f"Image file_id: {file_id}")
                    response = client.files.content(file_id)
                    with open("stock-image.png", "wb") as f:
                        f.write(response.read())


def delete_assistants(client=None):
    if client is None:
        client = create_client()
    assistants_list = client.beta.assistants.list()
    if len(assistants_list.data) == 0:
        print("No assistants found.")
    for a in assistants_list.data:
        assistant_deleted = client.beta.assistants.delete(a.id)
        print(f"Assistant deleted: {assistant_deleted}")


def print_run_steps(client: openai.OpenAI, thread, run, verbose=False):
    print("\nRun steps:")
    run_steps = client.beta.threads.runs.steps.list(
        thread_id=thread.id,
        run_id=run.id
    )
    for step in run_steps:
        print(f"\033[1m- Step {step.id}\033[0m")
        if verbose:
            details = step.step_details
            if isinstance(details, ToolCallsStepDetails):
                for tool_call in details.tool_calls:
                    if tool_call.type == "code_interpreter":
                        print("\tCode interpreter tool call. Src:")
                        print("```")
                        print(highlight(tool_call.code_interpreter.input, PythonLexer(), TerminalFormatter()))
                        print("```")
                        print("\tCode interpreter tool call output:")
                        pprint(tool_call.code_interpreter.outputs)


def execute_full_conversation():
    client = create_client()
    assistant = get_assistant(client)
    thread = create_thread(client)
    send_message_to_thread(client, thread,
                           "Retrieve the monthly time series data for the stock symbol 'AAPL' for April, May and June 2025.")
    execute_thread_run(client, assistant, thread)

    send_message_to_thread(client, thread,
                           "Make a visualization with the retrieved monthly stock data: a graph for stock prices and another one for stock volume.")
    run = execute_thread_run(client, assistant, thread)
    print_assistant_response(client, thread)
    print_run_steps(client, thread, run, verbose=True)
