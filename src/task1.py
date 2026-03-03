import os
import time

from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

from utils.helpers import AssistantArgs, get_or_create_assistant

print('::::::::::::::')
print('::: TASK 1 :::')
print('::::::::::::::')

# 1. Set up the Assistant
# print('\n::: Step 1 :::')
load_dotenv()

api_key = os.environ.get('OPENAI_API_KEY')
base_url = os.environ.get('OPENAI_BASE_URL')
client = OpenAI(api_key=api_key, base_url=base_url)

ASSISTANT_NAME = 'stock_analyzer_assistant'
ASSISTANT_INSTRUCTIONS = "You're an experienced stock analyzer assistant tasked with analyzing and visualizing stock market data."
ASSISTANT_MODEL = 'gpt-4o-mini'
assistant_params: AssistantArgs = {
  'name': ASSISTANT_NAME,
  'instructions': ASSISTANT_INSTRUCTIONS,
  'model': ASSISTANT_MODEL,
}
# 2. Validate Assistance existence
# print('\n::: Step 2 :::')
assistant = get_or_create_assistant(client, assistant_params)
print(f'---> Assistant retrieved or created: {assistant.id}')
# 3. Create a Thread object
# print('\n::: Step 3 :::')
thread = client.beta.threads.create()
print(f'---> Thread created with ID: {thread.id}')
# 4. Send a message to the Thread
# print('\n::: Step 4 :::')
initial_thread_role = 'user'
initial_thread_content = 'Tell me your name and instructions. YOU MUST Provide a DIRECT and SHORT response.'
message = client.beta.threads.messages.create(
  thread_id=thread.id,
  role=initial_thread_role,
  content=initial_thread_content
)
print(f'---> Message added to thread: {message.id}')
# 5. Execute a Run instance
# print('\n::: Step 5 :::')
run = client.beta.threads.runs.create(
  thread_id=thread.id,
  assistant_id=assistant.id
)
print(f'---> Run created with ID: {run.id}')
while run.status == 'in_progress' or run.status=='queued':
  time.sleep(1)
  run = client.beta.threads.runs.retrieve(
    thread_id=thread.id,
    run_id=run.id
  )
  print(f'---> Run status: {run.status}')
messages = client.beta.threads.messages.list(
  thread_id=thread.id
)
for msg in messages.data:
  if msg.role == 'assistant':
    print(f'---> Assistant Message: {msg.content[0].text.value}')
