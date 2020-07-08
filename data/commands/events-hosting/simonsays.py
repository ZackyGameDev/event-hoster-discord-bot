import discord
from discord.ext import commands

class SimonSays(commands.Cog):

    def __init__(self, client):
        self.client = client

    # To say something embeded in the simon says get_channel
    @commands.command(aliases=['simonsays', 'simonsay', 'simon-say', 'simon-says'])
    async def simon_says(self, ctx, *, to_say):
        await client.get_channel(get_channel_simonsays)
