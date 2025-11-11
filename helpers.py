def create_assistant(name, instructions, client, tools=None):
    assistant = find_assistant(name, client.beta.assistants.list())
    if assistant is None:
        assistant = client.beta.assistants.create(
            name=name,
            instructions=instructions,
            model="gpt-4o-mini",
            tools=tools
        )
        print(f"No matching `{name}` assistant found, creating a new assistant with ID: {assistant.id}")
    else:
        print(f"Matching `{name}` assistant found, using the first matching assistant with ID: {assistant.id}")
    return assistant


def find_assistant(name, assistants_list):
    for assistant in assistants_list.data:
        if assistant.name == name:
            return assistant
    return None