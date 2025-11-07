"""
Thread and message management service.

Handles thread creation, message operations, and run execution
for conversations with the Stock Analyzer assistant.
"""
from colorama import Fore, Style


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


def run_thread(client, assistant_id, thread_id):
    """
    Execute a run instance to process messages in a thread.
    Links the thread with the assistant and triggers processing of the user's
    message. The assistant will analyze the request and generate a response.
    :param client: The OpenAI client instance
    :param assistant_id: The assistant's unique identifier
    :param thread_id: The thread's unique identifier
    :return: The created run object
    """
    try:
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )
        print(f"{Fore.GREEN}Created run with ID: {Fore.YELLOW}{run.id}{Style.RESET_ALL}")
        return run
    except Exception as e:
        print(f"{Fore.RED}Error: Failed to run a thread.{Style.RESET_ALL}")
        print(f"Details: {e}")
        exit(1)
