'''
voice cog
~~~~~~~~~
Centralized voice management cog.
'''
'''
██╗   ██╗ ██████╗ ██╗ ██████╗███████╗  
██║   ██║██╔═══██╗██║██╔════╝██╔════╝    ____    ____     ____  
██║   ██║██║   ██║██║██║     █████╗    _/ ___\  /  _ \   / ___\ 
╚██╗ ██╔╝██║   ██║██║██║     ██╔══╝    \  \___ (  <_> ) / /_/  >
 ╚████╔╝ ╚██████╔╝██║╚██████╗███████╗   \___  > \____/  \___  / 
  ╚═══╝   ╚═════╝ ╚═╝ ╚═════╝╚══════╝       \/         /_____/                                                                                                 
'''

# Import libraries
import discord
from discord.ext import commands
import asyncio

# Import modules
from src.core import constants
from src.voice import tts

class Voice(commands.Cog):
    """
    Voice Cog
    ~~~~~~~~~
    Maintains all VC methods in a modular way.
    """
    
    def __init__(self, bot: discord.Bot):
        """
        Initialize the class.
        """
        self.bot = bot
    

    '''
    VC Methods
    '''

    async def verify(self, ctx) -> bool:
        """
        Verifies if the ctx is eligible.
        """
        # 1. Reject non-guild requests (DMs)
        if ctx.guild is None:
            await ctx.respond('i can only vc in servers', ephemeral=True)
            return False

        # 2. Reject if not in VC
        elif ctx.author.voice is None:
            await ctx.respond('you have to join vc first', ephemeral=True)
            return False
        
        # 3. Reject if already in VC
        elif ctx.guild.voice_client is not None:
            await ctx.respond('im already in vc', ephemeral=True)
            return False
                    
        # Passed!
        else:
            return True

    async def connect(self, ctx):
        """
        Connects to voice channel.
        """
        try:
            # Run verification
            if await self.verify(ctx):

                # Obtain channel
                channel = ctx.author.voice.channel
                # Connect to channel
                await channel.connect()
                await ctx.respond('ok ready now', ephemeral=True)
            
        except Exception as e:
            await ctx.respond(f"i think it broke: `{e}`", ephemeral=True)


    @discord.slash_command()
    async def vc(self, ctx):
        """
        Start a voice call.
        """
        await self.connect(ctx)


    '''
    Utility Methods
    '''

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """
        Handles state mismatches (zombie channels.)

        Ensures voice channel connections are robust.
        """
        # Check if member was bot
        if member == self.bot.user:
            
            # If change was a *disconnect*
            if (
                before.channel is not None and # was in VC
                after.channel is None # no longer in VC
                ):

                # Cleanup zombie channels if required
                if member.guild.voice_client is not None:
                    try:
                        await self.cleanup(member)
                    except Exception as e:
                        print(f'Could not cleanup channel: {e}')
    
    async def cleanup(self, member):
        """
        Cleanup zombie channel connections.
        """
        client = member.guild.voice_client

        # First disconnect the client from zombie channel
        await client.disconnect()

        # Then cleanup() zombie channel
        client.cleanup()

