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
        status   = discord.Status.idle,
        activity = discord.Activity(
        type     = discord.ActivityType.listening,
        name     = ATTR['current_song'][0],
        )
    )
    clear()
    print(f'Successfully logged in as @{bot.user}.')
    print()

'''
Reply to pings.
'''
@bot.event
async def on_message(message):
    # Ignore self messages
    if message.author == bot.user:
        return
    
    # Reply if mentioned
    if bot.user in message.mentions:
        user_message = utility.bot_mention_strip(message.content)

        # Catch empty messages
        if user_message == "":
            user_message = ATTR['name']

        try:
            bot_message = cognition.chat_response(user_message)
        except cognition.openai.error.OpenAIError:
            bot_message = ERROR_OPENAI
        
        # Catch empty messages
        if bot_message == "":
            bot_message = ERROR_OPENAI

        await message.reply(bot_message)


'''
Run the bot
'''
bot.run(DISCORD_BOT_TOKEN)
