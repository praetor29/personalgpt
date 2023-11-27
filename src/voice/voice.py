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
        print("verify() called")
        try: # for debugging!!
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
            
            # (!) Handle potential mismatch
            elif not await self.mismatch(ctx):
                return False
            
            # Passed! Return confirmation
            else:
                await ctx.respond('ok ready now', ephemeral=True)
                print('Passed verification!')
                return True
        except Exception as e:
            print(f"Exception in verify(): {e}")
            return False

    async def connect(self, ctx):
        """
        Connects to voice channel.
        """
        # Debug print
        print("connect() called")
        print(f"Dictionary state: {self.connections.get(ctx.guild.id)}")
        print(f"Discord.py state: {ctx.guild.voice_client}")
        
        try: # for debuggin!!
            # Run verification
            if await self.verify(ctx):

                # Obtain channel
                channel = ctx.author.voice.channel
                # Connect to channel
                await channel.connect()
        except Exception as e:
            print(f"Exception in connect(): {e}")


    @discord.slash_command()
    async def vc(self, ctx):
        """
        Start a voice call.
        """
        await self.connect(ctx)

    '''
    Utility Methods
    '''
    
    async def mismatch(self, ctx) -> bool:
        """
        Handles library vs dict state mismatch.
        
        Note: Something of a workaround!
        """
        print("mismatch() called")
        if (
            ctx.guild.voice_client is not None and
            self.connections.get(ctx.guild.id, None) is None
            ):
            print("Mismatch detected")
            try:
                await ctx.guild.voice_client.disconnect()
                print("Bot disconnected successfully")
                ctx.guild.voice_client.cleanup()
                print(f"Internal state after cleanup: {ctx.guild.voice_client}")
                await asyncio.sleep(1)
                print(f"Internal state after sleep: {ctx.guild.voice_client}")
                return True
            except Exception as e:
                await ctx.respond(f'i think it broke: `{e}`', ephemeral=True)
                print(f"Exception in mismatch(): {e}")
                return False
        print("No mismatch detected")
        return True

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        # Check if member was bot
        if member == self.bot.user:
            
            # If change was a disconnect
            if (
                before.channel is not None and # was in VC
                after.channel is None # no longer in VC
                ):
                # Remove connection from dict
                self.connections.pop(member.guild.id, None)

                print(f"Updated dictionary state: removed the entry")
            
            # If change was a connect
            elif (
                after.channel is not None # is now in VC/different VC
                ):
                # Add connection to dict
                self.connections[member.guild.id] = after.channel
                print(f"Updated dictionary state: {self.connections.get(member.guild.id)}")


                

