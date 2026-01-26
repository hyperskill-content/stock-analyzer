import time

from config import Config
from openai import OpenAI

# start open ai here
client = OpenAI(api_key=Config.api_key, base_url=Config.base_url)

def create_assistant(openai_client: OpenAI):
    return openai_client.beta.assistants.create(
        name=Config.assistant_name,
        instructions=Config.assistant_instruction,
        model=Config.assistant_model
    )

def get_assistant_when_exists(openai_client: OpenAI):
    assi_list = openai_client.beta.assistants.list()
    for assistant in assi_list:
        if assistant.name == Config.assistant_name:
            return assistant
    return None


def execute(openai_client: OpenAI):
    assi = get_assistant_when_exists(openai_client)
    assistant: openai_client.types.beta.assistant.Assistant
    if assi:
        assistant = assi
        print(f"Matching ", assistant.name," assistant found, using the first matching assistant with ID: ", assistant.id)
    else:
        assistant = create_assistant(openai_client)
        print(f"No matching ", Config.assistant_name," assistant found, creating a new assistant with ID: ", assistant.id)

    # create thread for conversation
    thread = client.beta.threads.create()
    print(f"Thread created with ID: {thread.id}")

    # add message to thread
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="Tell me your name and instructions. YOU MUST Provide a DIRECT and SHORT response."
    )
    print(f"Message added to thread: {message.id}")

    # run assistant in thread
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )

    print(f"Run initiated with ID: {run.id}")

    # Wait for the run to complete
    # while run.status == "queued" or run.status == "in_progress":
    #     time.sleep(1)
    #     run = client.beta.threads.runs.retrieve(
    #         thread_id=thread.id,
    #         run_id=run.id
    #     )
    #     print(f"Run status: {run.status}") --not in task1

    # Retrieve the messages from the thread
    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )

    # Display the assistant's response
    for message in messages.data:
        if message.role == "assistant":
            print(f"Assistant: {message.content[0].text.value}")




# program flow
execute(client)
