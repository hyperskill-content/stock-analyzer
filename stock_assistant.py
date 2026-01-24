from dotenv import load_dotenv
from openai import OpenAI
import os
import time

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
ASSISTANT_NAME = "stock_analyzer_assistant"

def validate_assistant():
    assistants = client.beta.assistants.list()
    for assistant in assistants.data:
        if assistant.name == ASSISTANT_NAME:
            return assistant.id
    return None

def create_assistant():
    assistant = client.beta.assistants.create(
        name=ASSISTANT_NAME,
        instructions="You're an experienced stock analyzer assistant tasked with analyzing and visualizing stock market data.",
        model="gpt-4o-mini"
    )
    return assistant.id

def create_thread_message(message_content):
    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=message_content,
    )
    return thread.id

def run_thread(assistant_id, thread_id):
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
    )
    return run.id

def get_response(thread_id, run_id):
    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        if run.status == "completed":
            break
        else:
            time.sleep(1)

    messages = client.beta.threads.messages.list(thread_id)
    for message in messages.data:
        if message.role == "assistant":
            return message.content[0].text.value
        else:
            return "No assistant response found."
    return None

def main():
    assistant_id = validate_assistant()
    if assistant_id:
        print(f"No matching `{ASSISTANT_NAME}` assistant found, creating a new assistant with ID: {assistant_id}")
    else:
        assistant_id = create_assistant()
        print(f"Matching `{ASSISTANT_NAME}` assistant found, using the first matching assistant with ID: {assistant_id}")

    thread_id = create_thread_message("Tell me your name and instructions. YOU MUST Provide a DIRECT and SHORT response.")
    print(f"Thread created with ID: {thread_id}")

    run_id = run_thread(assistant_id,thread_id)
    print(f"Run initiated with ID: {run_id}")

    assistant_response = get_response(thread_id, run_id)
    print(f"Assistant Response: {assistant_response}")


if __name__ == "__main__":
    main()