"""
Thread and message management service.

Handles thread creation, message operations, and run execution
for conversations with the Stock Analyzer assistant.
"""
from colorama import Fore, Style
import json
import time


# Functions
def get_thread(openai_client):
    """
    Create a new thread for conversation with the Assistant.
    A thread represents a conversation session where messages are exchanged
    between the user and the assistant. Each thread maintains its own context
    and message history.
    :param openai_client: The OpenAI client instance
    :return: The created thread object
    """
    try:
        thread = openai_client.beta.threads.create()
        print(f"{Fore.GREEN}Created thread with ID: {Fore.YELLOW}{thread.id}{Style.RESET_ALL}")
        return thread
    except Exception as e:
        print(f"{Fore.RED}Error: Failed to create thread.{Style.RESET_ALL}")
        print(f"Details: {e}")
        exit(1)


def add_message(client, thread_id, role, content):
    """
    Add a message to a thread.
    Creates and adds a new message to an existing thread. The message can be
    from a user or assistant role. Accepts either a MessageRole enum or a
    string value for the role parameter.
    :param client: The OpenAI client instance
    :param thread_id: The thread's unique identifier
    :param role: Message role (MessageRole enum or string: "user" or "assistant")
    :param content: The message content/text
    :return: The created message object
    """
    # Extract .value if a role is an enum, otherwise use it directly
    role_value = role.value if hasattr(role, 'value') else role

    try:
        message = client.beta.threads.messages.create(thread_id=thread_id, role=role_value, content=content)
        print(f"{Fore.GREEN}Thread message added with ID: {Fore.YELLOW}{message.id}{Style.RESET_ALL}")
        return message
    except Exception as e:
        print(f"{Fore.RED}Error: Failed to add message to thread.{Style.RESET_ALL}")
        print(f"Details: {e}")
        exit(1)


def run_thread(client, assistant_id, thread_id, available_functions=None):
    """
    Execute a run instance to process messages in a thread.
    Links the thread with the assistant and triggers processing of the user's message.
    If available_functions is provided, handles function calling.
    :param client: The OpenAI client instance
    :param assistant_id: The assistant's unique identifier
    :param thread_id: The thread's unique identifier
    :param available_functions: Optional dict mapping function names to Python functions
    :return: The created run object
    """
    # Create the run
    try:
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )
        print(f"{Fore.GREEN}Created run with ID: {Fore.YELLOW}{run.id}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error: Failed to run a thread.{Style.RESET_ALL}")
        print(f"Details: {e}")
        exit(1)

    # If no functions provided, return immediately
    if available_functions is None:
        return run

    # Poll the run status and handle function calls
    while True:
        try:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            print(f"{Fore.CYAN}Run status: {Fore.YELLOW}{run.status}{Style.RESET_ALL}")

            # Check if the run is completed
            if run.status == "completed":
                print(f"{Fore.GREEN}Run completed successfully!{Style.RESET_ALL}")
                break

            # Check if the run failed
            elif run.status == "failed":
                print(f"{Fore.RED}Run failed: {run.last_error}{Style.RESET_ALL}")
                break

            # Check if the run requires action (function calling)
            elif run.status == "requires_action":
                print(f"{Fore.MAGENTA}Run requires action - processing tool calls...{Style.RESET_ALL}")

                # Extract tool calls
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []

                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    print(f"{Fore.CYAN}Tool call ID: {Fore.YELLOW}{tool_call.id}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}Calling function: {Fore.YELLOW}{function_name}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}Arguments: {Fore.YELLOW}{function_args}{Style.RESET_ALL}")

                    # Execute the function
                    if function_name in available_functions:
                        function_to_call = available_functions[function_name]
                        function_response = function_to_call(**function_args)

                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": json.dumps(function_response)
                        })
                        print(f"{Fore.GREEN}Function executed successfully{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}Error: Function {function_name} not found{Style.RESET_ALL}")

                # Submit tool outputs back to the assistant
                try:
                    run = client.beta.threads.runs.submit_tool_outputs(
                        thread_id=thread_id,
                        run_id=run.id,
                        tool_outputs=tool_outputs
                    )
                    print(f"{Fore.GREEN}Tool outputs submitted{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}Error: Failed to submit tool outputs.{Style.RESET_ALL}")
                    print(f"Details: {e}")
                    break

            # Wait before polling again
            time.sleep(3)

        except Exception as e:
            print(f"{Fore.RED}Error: Failed to retrieve run status.{Style.RESET_ALL}")
            print(f"Details: {e}")
            break

    return run
