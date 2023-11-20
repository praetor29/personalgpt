'''
utility
~~~~~~~
A collection of utility functions.
'''
'''
██╗   ██╗████████╗██╗██╗     ██╗████████╗██╗   ██╗
██║   ██║╚══██╔══╝██║██║     ██║╚══██╔══╝╚██╗ ██╔╝
██║   ██║   ██║   ██║██║     ██║   ██║    ╚████╔╝ 
██║   ██║   ██║   ██║██║     ██║   ██║     ╚██╔╝  
╚██████╔╝   ██║   ██║███████╗██║   ██║      ██║   
 ╚═════╝    ╚═╝   ╚═╝╚══════╝╚═╝   ╚═╝      ╚═╝                                              
'''

# Import libraries
import os
import tiktoken

def clear():
    """
    Clears the console screen.

    This function uses the operating system's command to clear the console screen. 
    It detects the operating system and uses 'cls' for Windows ('nt') and 'clear' for Unix-based systems.
    """
    os.system('cls' if os.name == 'nt' else 'clear')

async def tokenize(input: str) -> int:
    """
    Tokenize strings using 'cl100k_base'.
    Works with gpt-4, gpt-3.5-turbo, text-embedding-ada-002.
    """
    encoding = tiktoken.get_encoding('cl100k_base').encode(input)
    tokens   = len(encoding)
    return tokens

    


