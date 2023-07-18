'''
+---------------------------------------------------------------+
 This file contains useful functions for coding quality of life.
+---------------------------------------------------------------+
'''

import os

def clear():
    '''
    Clears the screen.
    '''
    os.system('cls' if os.name == 'nt' else 'clear')

