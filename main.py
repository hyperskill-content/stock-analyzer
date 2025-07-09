import os
import warnings

from dotenv import load_dotenv
from openai import OpenAI


def main():
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("BASE_URL")
    client = OpenAI(
        api_key=openai_api_key,
        base_url=base_url
    )

    warnings.filterwarnings("ignore", category=DeprecationWarning)

    existing_assistants = client.beta.assistants.list()
    assistant_name = "stock_analyzer_assistant"
    assistant = next((assistant for assistant in existing_assistants.data if assistant.name == assistant_name), None)

    if assistant:
        print(
            f"Matching `{assistant_name}` assistant found, using the first matching assistant with ID: {assistant.id}")
    else:
        assistant = client.beta.assistants.create(
            name="stock_analyzer_assistant",
            instructions="You're an experienced stock analyzer assistant tasked with analyzing and visualizing stock market data.",
            model="gpt-4o-mini"
        )
        print(f"No matching `{assistant_name}` assistant found, creating a new assistant with ID: {assistant.id}")
    assistant_id = assistant.id

    thread = client.beta.threads.create()
    thread_id = thread.id
    print(f"Thread created with ID: {thread_id}")

    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content="Tell me your name and instructions. YOU MUST Provide a DIRECT and SHORT response."
    )

    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    print(f"Run initiated with ID: {run.id}")


if __name__ == "__main__":
    main()
