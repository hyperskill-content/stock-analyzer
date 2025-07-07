# Data Analysis

In this stage, you will enhance the assistant with the ability to perform data analysis on the retrieved stock data. This will involve integrating the Code Interpreter tool to analyze the data and developing prompts that instruct the assistant on how to interpret stock data, such as identifying trends, calculating ratios, key metrics, and more.

**Important Note:** Before adding additional tools like the Code Interpreter to your assistant, you need to first delete the old one and then recreate it with the new tools. The same applies to any modifications to the assistant; you can confirm this by checking in the assistant panel on the OpenAI website.

## Objectives

To complete this stage, you need to implement these steps:

### 1. Integrate Code Interpreter Tool
To enable the Code Interpreter functionality, pass the `code_interpreter` as a parameter in the `tools` attribute of the Assistant object. Based on the nature of the user request, the model determines when to utilize the Code Interpreter during a run.

### 2. Prompt the Assistant
Change the prompt message to make the assistant retrieve and analyze the stock data. Example prompts:

**Retrieval Prompt:**
```
Retrieve the monthly time series data for the stock symbol 'AAPL' for the latest 3 months.
```

**Analysis Prompt:**
```
Analyze the retrieved stock data and identify any trends, calculate ratios, key metrics, etc.
```

> **Note:** Sometimes, the assistant might attempt to generate an image response, which we will handle in the next stage. For now, you can request a text response only.

### 3. Print the Steps
Print the list of steps with their IDs to see the inputs and outputs of Code Interpreter. If you get an error regarding the rate limit exceeded (RPM), try to set a timeout for 20 seconds between runs.

## Mock Data (Alternative)

In case you are experiencing errors with the stock API, you can use the following mock data to pass this stage:

```python
def get_stock_info(stock_symbol):
    mock_data = {
        "Meta Data": {
            "1. Information": "Monthly Prices (open, high, low, close) and Volumes",
            "2. Symbol": "IBM",
            "3. Last Refreshed": "2024-03-11",
            "4. Time Zone": "US/Eastern"
        },
        "Monthly Time Series": {
            "2024-03-11": {
                "1. open": "185.4900",
                "2. high": "198.7300",
                "3. low": "185.1800",
                "4. close": "191.7300",
                "5. volume": "37816338"
            },
            "2024-02-29": {
                "1. open": "183.6300",
                "2. high": "188.9500",
                "3. low": "178.7500",
                "4. close": "185.0300",
                "5. volume": "88679550"
            },
            "2024-01-31": {
                "1. open": "162.8300",
                "2. high": "196.9000",
                "3. low": "157.8850",
                "4. close": "183.6600",
                "5. volume": "128121557"
            }
        }
    }
    return mock_data
```

## Useful resources 

### Docs 
[The Code Interpreter tool](https://platform.openai.com/docs/guides/tools-code-interpreter)    


## Examples

### Example 1: Sample Execution Log

```
Matching `stock_analyzer_assistant` assistant found, using the first matching assistant with ID: asst_ixRCiWze9eII7yiW48BGfysf

Thread created with ID: thread_MSsimX0szrKc8klb7Z8HDaj8

Run initiated with ID: run_hTEad7OLCwauL1x0njCXnBVs

Waiting for response from `stock_analyzer_assistant` Assistant. Elapsed time: 0.00 seconds

Tool call with ID and name: call_zFlM1aqjtfkqsNgszl4ruHeG retrieve_stock_data

Waiting for response from `stock_analyzer_assistant` Assistant. Elapsed time: 19.20 seconds

Done! Response received in 20.44 seconds.

Run initiated with ID: run_hTEad7OLCwauL1x0njCXnBVs
Assistant response: I have retrieved the monthly time series data for the stock symbol 'AAPL' for the latest 3 months. Here is a summary of the data:

- March 2024: Opened at $179.55, reached a high of $180.53, and closed at $170.73.
- February 2024: Opened at $183.98, reached a high of $191.05, and closed at $180.75.
- January 2024: Opened at $187.15, reached a high of $196.38, and closed at $184.40.

Analysis:
- Over the past 3 months, Apple Inc. (AAPL) stock prices have seen a slight decline from January to March 2024.
- The stock price showed volatility with fluctuating highs and lows during the analyzed period.
- The trading volume has been high, indicating significant interest and activity in the stock.

Further analysis can be conducted on historical trends, moving averages, and other financial ratios to gain deeper insights into the stock performance.

Step: step_vD9WQHVgRgCptyeVy6Gds68C
Step: step_uE5HihRpVnKlqOU6S8RxFKwF
```