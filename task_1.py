import os
from openai import OpenAI
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("BASE_URL")
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )
    
    assistant_name = "stock_analyzer_assistant"
    assistant_instructions = "You're an experienced stock analyzer assistant tasked with analyzing and visualizing stock market data."
    
    assistants = client.beta.assistants.list()
    existing_assistant = None
    
    for assistant in assistants.data:
        if assistant.name == assistant_name:
            existing_assistant = assistant
            break
    
    if existing_assistant:
        print(f"Matching `{assistant_name}` assistant found, using the first matching assistant with ID: {existing_assistant.id}")
        assistant_id = existing_assistant.id
    else:
        new_assistant = client.beta.assistants.create(
            name=assistant_name,
            instructions=assistant_instructions,
            model="gpt-4"
        )
        print(f"No matching `{assistant_name}` assistant found, creating a new assistant with ID: {new_assistant.id}")
        assistant_id = new_assistant.id
    
    thread = client.beta.threads.create()
    print(f"\nThread created with ID: {thread.id}")
    
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="Tell me your name and instructions. YOU MUST Provide a DIRECT and SHORT response."
    )
    
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id
    )
    print(f"\nRun initiated with ID: {run.id}")

if __name__ == "__main__":
    main()