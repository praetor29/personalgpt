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

        # Dictionary that holds all voice connections
        self.connections = {}
    
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
        elif self.connections.get(ctx.guild.id, None) is not None:
            await ctx.respond('im already in vc', ephemeral=True)
            return False
                    
        # Passed! Return confirmation
        else:
            await ctx.respond('ok ready now', ephemeral=True)
            return True

    async def connect(self, ctx):
        """
        Connects to voice channel.
        """
        # Run verification
        if await self.verify(ctx):

            # Obtain channel
            channel = ctx.author.voice.channel
            # Connect to channel
            try:
                await channel.connect()
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
        Maintains the connections dictionary and handles state mismatches (zombie channels.)

        Ensures voice channel connections are robust.
        """
        # Check if member was bot
        if member == self.bot.user:
            
            # If change was a *disconnect*
            if (
                before.channel is not None and # was in VC
                after.channel is None # no longer in VC
                ):

                # 1. Remove connection from dict
                self.connections.pop(member.guild.id, None)

                # 2. Cleanup potential zombie channels
                if (
                    member.guild.voice_client is not None and
                    self.connections.get(member.guild.id, None) is None
                    ):
                    # First disconnect the client from zombie channel
                    try:
                        await member.guild.voice_client.disconnect()
                    except Exception as e:
                        print(f'Could not disconnect from zombie channel: {e}')
                    # Then cleanup() zombie channel
                    try:
                        member.guild.voice_client.cleanup()
                    except Exception as e:
                        print(f'Could not cleanup zombie channel: {e}')
            
            # If change was a *connect*
            elif (
                after.channel is not None # is now in VC/different VC
                ):
                # Add connection to dict
                self.connections[member.guild.id] = after.channel
