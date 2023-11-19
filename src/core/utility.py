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

def clear():
    """
    Clears the console screen.

    This function uses the operating system's command to clear the console screen. 
    It detects the operating system and uses 'cls' for Windows ('nt') and 'clear' for Unix-based systems.
    """
    os.system('cls' if os.name == 'nt' else 'clear')




