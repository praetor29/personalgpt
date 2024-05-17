"""
utility
~~~~~~~
A collection of utility functions.
"""

"""
██╗   ██╗████████╗██╗██╗     ██╗████████╗██╗   ██╗
██║   ██║╚══██╔══╝██║██║     ██║╚══██╔══╝╚██╗ ██╔╝
██║   ██║   ██║   ██║██║     ██║   ██║    ╚████╔╝ 
██║   ██║   ██║   ██║██║     ██║   ██║     ╚██╔╝  
╚██████╔╝   ██║   ██║███████╗██║   ██║      ██║   
 ╚═════╝    ╚═╝   ╚═╝╚══════╝╚═╝   ╚═╝      ╚═╝                                              
"""

# Import libraries
from os import system, name
import tiktoken
from pathlib import Path


def clear():
    """
    Clears the console screen using OS specific command.
    - Windows: 'cls'
    - POSIX  : 'clear'
    """
    system("cls" if name == "nt" else "clear")


async def tokenize(input: str) -> int:
    """
    Tokenize strings using tiktoken's 'cl100k_base'.
    Works with gpt-4 et al. and embeddings models.
    """
    encoding = tiktoken.get_encoding("cl100k_base").encode(input)
    tokens = len(encoding)
    return tokens


async def tokenize_lite(input: str) -> int:
    """
    Tokenize strings using a simple approximation:
    "1 token = 4 characters."
    """
    tokens = len(input) // 4
    return tokens

