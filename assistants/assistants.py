from typing import Optional
from config import Config
from openai import OpenAI


def create_assistant(openai_client: OpenAI, tools: Optional[list] | None):
    assi = find_assistant_by_name(openai_client)
    assistant: openai_client.types.beta.assistant.Assistant
    if assi:
        assistant = assi
        print(
            f"Matching `{assistant.name}` assistant found, "
            f"using the first matching assistant with ID: {assistant.id}"
        )
    else:
        assistant = openai_client.beta.assistants.create(
            name=Config.assistant_name,
            instructions=Config.assistant_instruction,
            model=Config.assistant_model,
            tools=tools
        )
        print(
            f"No matching `{assistant.name}` assistant found, "
            f"creating a new assistant with ID: {assistant.id}"
        )
    return assistant



def get_assistant(openai_client: OpenAI, assistant_id: str):
    return openai_client.beta.assistants.retrieve(assistant_id)

def find_assistant_by_name(openai_client: OpenAI):
    assi_list = openai_client.beta.assistants.list()
    for assistant in assi_list:
        if assistant.name == Config.assistant_name:
            return assistant
    return None

def delete_assistant(openai_client: OpenAI, assistant_id: str):
    return openai_client.beta.assistants.delete(assistant_id)