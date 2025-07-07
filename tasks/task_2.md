# Data Retrieval

This stage aims to enable the assistant to fetch and handle JSON data from a stock market API. This involves integrating prompt engineering to create queries for the assistant, ensuring accurate data retrieval from the stock API. The API you need to use is [**Alpha Vantage**](https://www.alphavantage.co/support/#api-key). Check the link to see how it's used.

## Objectives

Your task is to add the assistant the ability to fetch stock data and display it. Here's a step-by-step guide to achieve this:

### 1. Set Up the Stock API
Use the API key to retrieve stock data. For example, retrieve the daily time series data for the stock symbol 'AAPL'.

**Available Function Parameters:**
- `"TIME_SERIES_INTRADAY"`
- `"TIME_SERIES_DAILY"`
- `"TIME_SERIES_WEEKLY"`
- `"TIME_SERIES_MONTHLY"`

The `symbol` parameter is the stock symbol of your choice. This regular function can send a request to the stock API URL. The assistant will use this function and pass the necessary arguments.

### 2. Define the Tools
Next, define a tools list and pass it to `assistants.create()`. You can see an example here. The function you define here should match the Python function from the previous step. This means that the parameters defined here in the tools are the parameters for the Python function. This is how GPT understands how to use the function.

### 3. Trigger the Action with a Prompt
You can try with different prompts; however, in this case, run this prompt to trigger the function calling:

```
Retrieve and show the latest daily time series data for the stock symbol 'AAPL'.
```

### 4. Handle the `requires_action` State
After triggering the function calling, the run object will enter a `requires_action` state. This is where you execute the Python function to call the stock API. 

**Key Points:**
- To execute the function, you need to use the function name, arguments, and function ID
- You can find them in `submit_tool_outputs`
- Print the tool_call IDs with each function call
- The assistant may call the function multiple times, in that case you need to handle it with a loop

### 5. Submit Function Response
Once the function has been executed, return its output to the assistant. Following this, the assistant will proceed with the conversation, integrating the response from the function.

You can print the assistant's responses at the end.

## Important Notes

> **Warning:** Delete the assistants from the previous stage and re-create them to use the new tools. In case old assistants are used, they might not function as expected.

## API Management Commands

### Get List of Assistants
```bash
curl -X 'GET' 'https://litellm.aks-hs-prod.int.hyperskill.org/assistants' \
  -H 'accept: application/json' \
  -H "Authorization: Bearer <litellm secret key>"
```

### Delete Assistant by ID
```bash
curl -X 'DELETE' 'https://litellm.aks-hs-prod.int.hyperskill.org/assistants/asst_<id>' \
  -H 'accept: application/json' \
  -H "Authorization: Bearer <litellm secret key>"
```

Ensure that your program outputs all necessary information, including:
- The creation of the assistant
- The Thread creation
- The Run instance
- Following the specified formats for IDs and messages

## Useful resources 

### Topics 
[Function calls with chat completions](https://hyperskill.org/learn/step/45477)   
[Function calling with Assistant](https://hyperskill.org/learn/step/46435)   
[Requests: retrieving data](https://hyperskill.org/learn/step/8603)   
[More dictionary methods](https://hyperskill.org/learn/step/36298)


## Examples

### Example 1: Retrieving Stock Data with Function Calling

```
Matching `stock_analyzer_assistant` assistant found, using the first matching assistant with ID: asst_iahCFboNCzF7i25pj3yYVjfa
Thread created with ID: thread_A4PKceRZrEUDLdw2F6t87ILY
Run initiated with ID: run_LyCPPQ7Q8QjA0uifQdmysZ1w
Waiting for response from `stock_analyzer_assistant` Assistant. Elapsed time: 4.92 seconds
Tool call with ID and name:  call_zFlM1aqjtfkqsNgszl4ruHeG retrieve_stock_data
Done! Response received in 6.25 seconds.

Run initiated with ID: run_LyCPPQ7Q8QjA0uifQdmysZ1w
Assistant response: Here is the latest daily time series data for the stock symbol 'AAPL':

- Date: 2024-03-07
  - Open: $169.1500
  - High: $170.7300
  - Low: $168.4900
  - Close: $169.0000
- Volume: 71,765,061

This data is as of the most recent update.
```