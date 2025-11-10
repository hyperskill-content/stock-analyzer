"""
Main Helper Functions Module
Provides utility functions for main script execution flow
"""

# Imports
from colorama import Fore, Style


# Functions
def main_initialization():
    """
    Display the task initialization banner.
    Prints a formatted header indicating the start of Task.
    Uses color formatting to enhance visibility in the terminal output.
    """
    print()
    print("=" * 40)
    print(f"{Fore.CYAN}      TASK 3: Data Analysis{Style.RESET_ALL}")
    print("=" * 40)
    print()


def main_end():
    """
    Display the task completion banner.
    Prints a formatted footer indicating the completion of Task.
    Uses color formatting to enhance visibility in the terminal output.
    """
    print()
    print("=" * 40)
    print(f"{Fore.CYAN}      TASK 3 Complete{Style.RESET_ALL}")
    print("=" * 40)
    print()
