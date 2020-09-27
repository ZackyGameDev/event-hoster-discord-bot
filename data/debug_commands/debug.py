import discord
import os
from discord.ext import commands

def author_is_zacky(ctx):
    return ctx.author.id == 625987962781433867

class DebugCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("Debug Commands are currently none")
        
    @commands.command()
    @commands.check(author_is_zacky)
    async def git_pull(self, ctx):
        os.system("git pull")
    
def setup(client):
    client.add_cog(DebugCommands(client))