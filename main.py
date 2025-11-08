import os
import openai
import helpers

### Setup
api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key, base_url="https://litellm.aks-hs-prod.int.hyperskill.org/openai")
STOCK_ANALYZER_ASSISTANT_ID = "stock_analyzer_assistant"
STOCK_ANALYZER_ASSISTANT_INSTRUCTIONS = "You're an experienced stock analyzer assistant tasked with analyzing and visualizing stock market data."

### 1. Set Up the Assistant
stock_analyzer_assistant = helpers.create_assistant(
    name=STOCK_ANALYZER_ASSISTANT_ID,
    instructions=STOCK_ANALYZER_ASSISTANT_INSTRUCTIONS,
    client=client
)

### 2. Validate Assistant Existence
# done inside the create_assistant function in step 1

### 3. Create a Thread Object
thread = client.beta.threads.create()
print(f"Thread created with ID: {thread.id}")


### 4. Send a Message to the Thread
client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Tell me your name and instructions. YOU MUST Provide a DIRECT and SHORT response."
)

### 5. Execute a Run Instance
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=stock_analyzer_assistant.id,
)
print(f"Run initiated with ID: {run.id}")
