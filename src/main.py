'''
+------------------------------------------------------------------+
| Title      : Personal GPT                                        |
| Author     : Pranav Chiploonkar (@praetor29)                     |
+------------------------------------------------------------------+
| Description: This program runs the core loop of the discord bot. |
+------------------------------------------------------------------+
'''

# Import functions and constants
import constants
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
        status   = discord.Status.idle,
        activity = discord.Activity(
        type     = discord.ActivityType.listening,
        name     = constants.SONG,
        )
    )
    clear()
    print(f'Successfully logged in as {bot.user}.')
    print()

'''
Bot functioning
'''
@bot.event
async def on_message(message):   

    # channel_id     = message.channel.id,
    # author         = message.author,
    # author_id      = message.author.id,
    # chat_message   = message.clean_content
    
    # Ignore own messages
    if message.author == bot.user:
        return

    # Reply if mentioned
    if bot.user in message.mentions:
        # Strip prefix
        bot_prefix   = f'<@{constants.BOT_ID}>'
        user_message = message.content.removeprefix(bot_prefix).strip()

        # Catch empty messages
        if not user_message:
            user_message = bot.user.name

        try:
            gpt_response = await cognition.chat_response(user_message)
        except cognition.openai.error.OpenAIError:
            gpt_response = constants.ERROR_OPENAI

        print(gpt_response)
        
        payload = utility.splitter(gpt_response)
        for packet in payload:
            await message.reply(packet)

'''
Run the bot
'''
bot.run(constants.DISCORD_BOT_TOKEN)
