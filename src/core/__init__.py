'''
core modules
~~~~~~~~~~~~
- bot.py
- constants
- utility               
'''
# Import libraries
import os
from dotenv import load_dotenv

# Load environment
env_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', '.env')
load_dotenv(env_path)