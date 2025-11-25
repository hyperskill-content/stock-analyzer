# Assistant Creation

## Description

In the project's first stage, you'll create the Stock Analyzer Assistant by giving it a name and instructions. You'll also create a Thread object where you will be able to interact and communicate with the assistant, and finally, you'll start a Run instance to execute the assistant and process the user's prompts. This basic configuration will set the stage for the assistant's future development and functionality.

## Objectives

Your primary task is initializing and configuring the Stock Analyzer Assistant using the OpenAI API. This involves the creation of an assistant instance, setting up a communication thread, and initiating a run to execute the instructions from a simple prompt.

> ⚠️ **Important Security Note:**
> This project involves the use of private keys (OpenAI API keys) and .env files. Please ensure you **DO NOT** expose your keys by hardcoding them directly into the solution. Instead, always reference them securely from your .env file. Additionally, do not include your .env file in your project submission. Double-check your code for any accidental key exposure before submission. If sharing code snippets, mask sensitive values. You can use this package to load a .env file.

Before starting, create the .env file from a template:
```bash
cp .env.template .env
```

**LiteLLM Proxy Configuration:**
In case you are using the LiteLLM proxy, set the `base_url` parameter of the OpenAI client to `https://litellm.aks-hs-prod.int.hyperskill.org/openai`

## Implementation Steps

### 1. Set Up the Assistant
Begin by configuring the assistant. Set a name and instructions for the assistant using the `assistants.create()` method.

**Configuration:**
- **Name:** `stock_analyzer_assistant`
- **Instructions:**
```
You're an experienced stock analyzer assistant tasked with analyzing and visualizing stock market data.
```

### 2. Validate Assistant Existence
Implement a check to determine if an assistant named `stock_analyzer_assistant` already exists. If it does, use the existing assistant; if not, proceed to create a new assistant with this name. You can achieve this by leveraging the `assistants.list()` method to search for existing assistants.

### 3. Create a Thread Object
Once the assistant setup is confirmed, create a Thread object. This thread serves as a conversation context where the assistant receives tasks and returns responses. Utilize the `threads.create()` method to accomplish this step.

### 4. Send a Message to the Thread
Make use of the `threads.messages.create()` method to send a message to the thread. You can send any message you want as the response from the assistant won't be checked, but we suggest that you send a message with a short prompt like:

```
Tell me your name and instructions. YOU MUST Provide a DIRECT and SHORT response.
```

### 5. Execute a Run Instance
Finally, execute a Run instance by linking the thread with the assistant ID. This action triggers the assistant's processing of the user's request. The execution can be initiated using the `threads.runs.create()` method with the thread and assistant ID information.

Ensure that your program outputs all necessary information, including:
- The creation of the assistant (or confirmation of existing assistant)
- The Thread creation
- The Run instance initiation
- Following the specified formats for IDs and messages

## Useful resources 

### Topics 
[Introduction to the Assistants API](https://hyperskill.org/learn/step/45396)
### Docs
[Assistants API deep dive](https://platform.openai.com/docs/assistants/deep-dive)    
[Notice on the Responses API](https://platform.openai.com/docs/guides/responses-vs-chat-completions)    

As of late 2025, the Responses API doesn't have full feature parity. The main blocker is that you can't programmatically create or manage assistants (called "Prompts" in the new API) — they can only be created through the Dashboard UI. The Responses API also has limited conversation history management compared to the thread-based system we rely on, and lacks equivalents for tool resources configuration. We'll migrate once the necessary features are available, well before the August 2026 deadline.   

## Examples

### Example 1: Creating and Executing New Assistant

When you run the code, the Assistant should be created (if it does not exist), and a Thread should be initiated. After sending a message to the Thread object, a Run instance should be executed to start the analysis:

```
No matching `stock_analyzer_assistant` assistant found, creating a new assistant with ID: asst_t03xkYG47OcKmt2wNP6CPOiY

Thread created with ID: thread_FFOOs1l4M4GT8cgMIjan7nHn

Run initiated with ID: run_xyFXFGkpTpaEb1P9MHlyDt4d
```

### Example 2: Using Existing Assistant

If the Assistant already exists, your program should use the existing `stock_analyzer_assistant` to create a Thread and execute the Run instance:

```
Matching `stock_analyzer_assistant` assistant found, using the first matching assistant with ID: asst_t03xkYG47OcKmt2wNP6CPOiY

Thread created with ID: thread_EEOOs1l4M4GT8cgMIjan7nHn

Run initiated with ID: run_abFXFGkpTpaEb1P9MHlyDt4d
```

