'''
+------------------------------------------------+
 This file handles memory and context management.
+------------------------------------------------+
'''

from constants import *
import utility

class Queue:
    '''
    Message queueing technology.
    '''
    def __init__(self, max_tokens: int):
        '''Initialize queue'''
        self.queue = []
        self.total_tokens = 0
        self.max_tokens = max_tokens

    def enqueue(self, chat_message: str, author: str, author_id: int):
        '''Add to queue.'''

        # Calculate message tokens
        tokens = utility.tokenizer(chat_message, None)

        # Dequeue until new message fits
        while (self.total_tokens + tokens) > self.max_tokens:
            self.dequeue()
        
        metadata = {
                'tokens'    : tokens,
                'timestamp' : utility.current_date(),
                'author'    : author,
                'author_id' : author_id,
                'message'   : chat_message,
        }

        self.queue.append(metadata)
        self.total_tokens += tokens

    def dequeue(self) -> dict:
        '''Push out of queue.'''
        if self.queue:
            metadata = self.queue.pop(0)
            self.total_tokens -= metadata['tokens']
            return metadata

    def get_messages(self) -> list:
        '''Returns a list of messages in queue.'''
        messages = []
        for metadata in self.queue:
            tokens = self.total_tokens
            author    = metadata['author']
            message   = metadata['message']
            messages.append(f'{tokens} | {author}: {message}')
        return messages

class ShortTermMemory:
    '''
    Handles short term memory per channel.
    '''
    def __init__(self):
        '''Initialize short-term memory dictionary.'''
        self.short_mem = {}

    def update_memory(self, channel_id: int, author: str, author_id: int, chat_message: str):
        '''Update the short-term memory for a given channel.'''
        
        # If channel entry not exist
        if channel_id not in self.short_mem:
            self.short_mem[channel_id] = Queue(SHORT_MEM_MAX)
        
        # Enqueue
        self.short_mem[channel_id].enqueue(chat_message, author, author_id)
