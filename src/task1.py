import os
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

from utils.helpers import AssistantArgs, get_or_create_assistant, delete_assistants

print('::: TASK 1 :::')

# 1. Set up the Assistant

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
assistant = get_or_create_assistant(client, assistant_params)

# 3. Create a Thread object
thread = client.beta.threads.create()

# 4. Send a message to the Thread
initial_thread_role = 'user'
initial_thread_content = 'Tell me your name and instructions. YOU MUST Provide a DIRECT and SHORT response.'
client.beta.threads.messages.create(
  thread_id=thread.id,
  role=initial_thread_role,
  content=initial_thread_content
)

# 5. Execute a Run instance