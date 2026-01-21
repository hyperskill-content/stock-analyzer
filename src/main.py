import os
import time

import dotenv
from openai import OpenAI

dotenv.load_dotenv()
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url=os.environ.get("BASE_URL")
)

isCreated = False
assistant = None
for assistant in client.beta.assistants.list().data:
    if assistant.name == "stock_analyzer_assistant":
        isCreated = True
        print("Stock Market Analyzer Assistant already exists with ID:", assistant.id)
        break

if not isCreated:
    stock_analyzer_assistant = client.beta.assistants.create(
        instructions="You are a stock market analysis assistant. Provide insights and analysis on stock market trends based on user queries.",
        model="gpt-4o-mini",
        name="stock_analyzer_assistant",
        tools=[{"type": "code_interpreter"}],
    )
    print("Stock Market Analyzer Assistant created with ID:", stock_analyzer_assistant.id)

empty_thread = client.beta.threads.create()
print("Empty thread created with ID:", empty_thread.id)
thread_message = client.beta.threads.messages.create(
    empty_thread.id,
    role="user",
    content="Tell me your name and instructions. YOU MUST Provide a DIRECT and SHORT response."
)
print(thread_message)
run = client.beta.threads.runs.create(
    empty_thread.id,
    assistant_id=assistant.id
)
print("Run created with ID:", run.id)
print("Run details:", run)
while run.status in ("queued", "in_progress"):
    print("Run status:", run.status)
    time.sleep(1)
    run = client.beta.threads.runs.retrieve(thread_id=empty_thread.id, run_id=run.id)
print("Final Run status:", run.status)
print("Final Run details:", run)
