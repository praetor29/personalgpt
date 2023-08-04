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

# Initialize ShortTermMemory
ShortTermMemory = memory.ShortTermMemory()

@bot.event
async def on_message(message):   

    '''Response loop when mentioned.'''
    if bot.user in message.mentions:
        # Ignore own messages
        if message.author == bot.user:
            return
        
        # Strip prefix
        bot_prefix   = f'<@{bot.user.id}>'
        user_message = message.content.removeprefix(bot_prefix).strip()

        # Catch empty messages
        if not user_message:
            user_message = bot.user.name

        try:
            gpt_response = await cognition.chat_response(user_message)
        except cognition.openai.error.OpenAIError:
            gpt_response = constants.ERROR_OPENAI
               
        payload = utility.splitter(gpt_response)
        for packet in payload:
            await message.reply(packet)

    '''Updating ShortTermMemory.'''
    if message.author != bot.user:
        # Pushes user package
        package_user = {
            'channel.id' :  message.channel.id,
            'author'     : (message.author.id, message.author.name),
            'message'    :  message.clean_content,
        }
        await ShortTermMemory.add(package=package_user)
    
    # Pushes bot package
    if bot.user in message.mentions:
        # Ignore own messages
        if message.author == bot.user:
            return
        
        package_bot  = {
            'channel.id' :  message.channel.id,
            'author'     : (bot.user.id, bot.user.name),
            'message'    :  gpt_response,
        }
        await ShortTermMemory.add(package=package_bot)

    buffer = await ShortTermMemory.read(id=message.channel.id)
    clear()
    print(buffer)

'''
Run the bot
'''
bot.run(constants.DISCORD_BOT_TOKEN)
