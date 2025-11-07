import os
from openai import OpenAI
from dotenv import load_dotenv

def start_assistant():
    # Load environment variables from .env file
    load_dotenv()

    # Retrieve the OpenAI API key from environment variables
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    base_url = os.getenv("BASE_URL")
    if not base_url:
        raise ValueError("OPENAI_API_URL not found in environment variables")

    # Initialize the OpenAI client with the API key and base URL
    client = OpenAI(api_key=api_key, base_url=base_url)

    assistant_name = "stock_analyzer_assistant"

    list_assistants = client.beta.assistants.list().data
    assistant_id = None

    for assistant in list_assistants:
        if assistant.name == assistant_name:
            assistant_id = assistant.id
            print(f"Matching `{assistant_name}` assistant found, using the first matching assistant with ID: {assistant.id}")
            break

    if not assistant_id:
        assistant = client.beta.assistants.create(
            name=assistant_name,
            instructions="You're an experienced stock analyzer assistant tasked with analyzing and visualizing stock market data.",
            model="gpt-4"
        )
        print(f"No matching `{assistant_name}` assistant found, creating a new assistant with ID: {assistant.id}")
        assistant_id = assistant.id

    thread = client.beta.threads.create()
    print(f"Thread created with ID: {thread.id}")

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="Tell me your name and instructions. YOU MUST Provide a DIRECT and SHORT response."
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id
    )

    print(f"Run initiated with ID: {run.id}")


if __name__ == "__main__":
    start_assistant()
