'''
+------------------------------------------------------------------+
| Title      : Personal GPT                                        |
| Author     : Pranav Chiploonkar (@praetor29)                     |
+------------------------------------------------------------------+
| Description: This program runs the core loop of the discord bot. |
+------------------------------------------------------------------+
'''

# Import functions and constants
from constants import *
from utility import clear
import utility
import cognition
import discord
import memory

'''
Declare intents
'''
intents = discord.Intents.default()
intents.message_content = True

'''
Initialize discord bot
'''
bot = discord.Client(intents=intents)

'''
Confirm login
Change status and activity
'''
@bot.event
async def on_ready():
    await bot.change_presence(
        status   = discord.Status.online,
        activity = discord.Activity(
        type     = discord.ActivityType.listening,
        name     = 'THE SIXTH LIE「ラストページ」',
        )
    )
    clear()
    print(f'Successfully logged in as {bot.user}.')
    print()

'''
Initialize ShortTermMemory class
'''
ShortTermMemory = memory.ShortTermMemory()

'''
Bot functioning
'''
@bot.event
async def on_message(message):   

    # ShortTermMemory
    ShortTermMemory.update_memory(
        channel_id     = message.channel.id,
        author         = message.author,
        author_id      = message.author.id,
        chat_message   = message.clean_content
    )
    
    # Print queue
    channel_queue = ShortTermMemory.short_mem.get(message.channel.id)
    if channel_queue:
        messages = channel_queue.get_messages()
        
        clear()
        for item in messages:
            print(item)
    
    # Ignore own messages
    if message.author == bot.user:
        return

    # Reply if mentioned
    if bot.user in message.mentions:
        user_message = message.content.removeprefix(f'<@{BOT_ID}>').strip()

        # Catch empty messages
        if not user_message:
            user_message = bot.user.name

        try:
            bot_message = cognition.chat_response(user_message)
        except cognition.openai.error.OpenAIError:
            bot_message = ERROR_OPENAI
        
        # Catch empty messages
        if not bot_message:
            bot_message = ERROR_OPENAI
        
        await message.reply(bot_message)


'''
Run the bot
'''
bot.run(DISCORD_BOT_TOKEN)
