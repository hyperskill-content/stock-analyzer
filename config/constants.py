"""
Configuration constants for the Stock Analyzer Assistant.

Contains assistant configuration, model settings, and enumerations
for message roles used throughout the application.
"""

from enum import Enum

ASSISTANT_MODEL = "gpt-4o-mini"
ASSISTANT_NAME = "stock_analyzer_assistant"
ASSISTANT_INSTRUCTION = "You're an experienced stock analyzer assistant tasked with analyzing and visualizing stock market data."
ASSISTANT_USER_MESSAGE = "Tell me your name and instructions. YOU MUST Provide a DIRECT and SHORT response."


class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"
