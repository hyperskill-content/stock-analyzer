import openai
import dotenv
import os
import time

from openai.types.beta import Assistant

dotenv.load_dotenv()

client = openai.OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url=os.environ.get("BASE_URL")
)


def get_assistant():
    assistants_list = client.beta.assistants.list()
    for a in assistants_list.data:
        if a.name == "stock_analyzer_assistant":
            print(
                f"Matching `stock_analyzer_assistant` assistant found, using the first matching assistant with ID: {a.id}")
            return a

    new_assistant = client.beta.assistants.create(
        instructions="You're an experienced stock analyzer assistant tasked with analyzing and visualizing stock market data.",
        name="stock_analyzer_assistant",
        model="gpt-4o-mini"
    )
    print(
        f"No matching `stock_analyzer_assistant` assistant found, creating a new assistant with ID: {new_assistant.id}")
    return new_assistant

def create_thread():
    thread = client.beta.threads.create()
    print(f"Thread created with ID: {thread.id}")
    return thread


def send_message_to_thread(thread, text):
    user_message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=text
    )
    print(f"Message added to thread: {user_message.id}")
    print(f"User message: {user_message.content[0].text.value}")


def execute_thread_run(assistant, thread):
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )
    print(f"Run initiated with ID: {run.id}")

    while run.status == "queued" or run.status == "in_progress":
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        # print(f"Run status: {run.status}")


def print_assistant_response(thread):
    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )
    for message in messages.data:
        if message.role == "assistant":
            print(f"Assistant: {message.content[0].text.value}")


def main():
    assistant = get_assistant()
    thread = create_thread()
    send_message_to_thread(thread, "Tell me your name and instructions. YOU MUST Provide a DIRECT and SHORT response.")
    execute_thread_run(assistant, thread)
    print_assistant_response(thread)


if __name__ == '__main__':
    main()
