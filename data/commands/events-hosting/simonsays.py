import discord
from discord.ext import commands

class SimonSays(commands.Cog):

    def __init__(self, client):
        self.client = client

    # To submit the id's in the database
    