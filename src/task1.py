import os
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

from utils.helpers import AssistantProps, get_or_create_assistant, delete_assistants

print('::: TASK 1 :::')

# 1. Set up the Assistant

load_dotenv()

api_key = os.environ.get('OPENAI_API_KEY')
base_url = os.environ.get('OPENAI_BASE_URL')
client = OpenAI(api_key=api_key, base_url=base_url)

ASSISTANT_NAME = 'stock_analyzer_assistant'
ASSISTANT_INSTRUCTIONS = "You're an experienced stock analyzer assistant tasked with analyzing and visualizing stock market data."
ASSISTANT_MODEL = 'gpt-4o-mini'
assistant_params: AssistantProps = {
  'name': ASSISTANT_NAME,
  'instructions': ASSISTANT_INSTRUCTIONS,
  'model': ASSISTANT_MODEL,
}
# 2. Validate Assistance existence
assistant = get_or_create_assistant(client, assistant_params)
print(f'###\n--- [ GOT ASSISTANT ] => \n=== {assistant.id} // {assistant.name}\n###')
# delete_assistants_by_name(client, ASSISTANT_NAME)
# asst_list = client.beta.assistants.list()
# print(f'>>> {len(asst_list.data)} \n{client.beta.assistants.list()}')

# 3. Create a Thread object
# 4. Send a message to the Thread
# 5. Execute a Run instance