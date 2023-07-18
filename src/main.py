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
        name     = 'i-mage',
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
    
    if bot.user in message.mentions:
        await message.reply("Hello World")


'''
Run the bot
'''
bot.run(DISCORD_BOT_TOKEN)
