import discord
from discord.ext import commands

class DebugCommands(commands.Cog):
    def __init__(self):
        self.client = client
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("Debug Commands are currently none")
    
def setup(client):
    client.add_cog(DebugCommands(client))