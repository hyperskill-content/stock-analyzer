from typing import TypedDict

from openai import OpenAI
from openai.types.beta.assistant import Assistant


class AssistantArgs(TypedDict):
    name: str
    instructions: str
    model: str


def get_or_create_assistant(client: OpenAI, props: AssistantArgs) -> Assistant:
    assistant = None
    assistant_name = props["name"]
    assistant_instructions = props["instructions"]
    assistant_model = props["model"]
    current_assistants = client.beta.assistants.list()
    for asst in current_assistants:
        if asst.name == assistant_name:
            assistant = asst
            break
    if not assistant:
        assistant = client.beta.assistants.create(
            name=assistant_name,
            instructions=assistant_instructions,
            model=assistant_model,
        )
    return assistant


def delete_assistants_by_name(client: OpenAI, assistant_name: str) -> None:
    assistants = client.beta.assistants.list()
    for asst in assistants:
        if asst.name == assistant_name:
            client.beta.assistants.delete(asst.id)
