'''
+------------------------------------------------+
 This file contains error handling functionality.
+------------------------------------------------+
'''
import os
import json
from openai.error import (
    APIError,
    APIConnectionError,
    Timeout,
    RateLimitError,
    InvalidRequestError,
    AuthenticationError,
    ServiceUnavailableError,
)
from discord.errors import (
    NotFound,
    Forbidden,
    HTTPException,
    LoginFailure,
)

# Import error messages
with open(os.path.join('errors', 'messages.json'), 'r') as file:
    messages = json.load(file)
     
def handle_exception(exception: Exception) -> str:
    '''
    PersonalGPT Error Handling:
    discord, openai, and generic exceptions.
    '''
    if   isinstance(exception, APIError):
        return messages["openai"]["APIError"]
    elif isinstance(exception, APIConnectionError):
        return messages["openai"]["APIConnectionError"]
    elif isinstance(exception, Timeout):
        return messages["openai"]["Timeout"]
    elif isinstance(exception, RateLimitError):
        return messages["openai"]["RateLimitError"]
    elif isinstance(exception, InvalidRequestError):
        return messages["openai"]["InvalidRequestError"]
    elif isinstance(exception, AuthenticationError):
        return messages["openai"]["AuthenticationError"]
    elif isinstance(exception, ServiceUnavailableError):
        return messages["openai"]["ServiceUnavailableError"]
    elif isinstance(exception, NotFound):
        return messages["discord"]["NotFound"]
    elif isinstance(exception, Forbidden):
        return messages["discord"]["Forbidden"]
    elif isinstance(exception, HTTPException):
        return messages["discord"]["HTTPException"]
    elif isinstance(exception, LoginFailure):
        return messages["discord"]["LoginFailure"]
    else:
        return f"Unhandled exception type: {type(exception).__name__}"