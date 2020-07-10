import discord
from discord.ext import commands
import os

client = commands.Bot(command_prefix='z!', case_insensitive=True)
client.remove_command('help')

@client.event
async def on_ready():
    for file in os.listdir('./data'):
        if file.endswith('.py'):
            file = file.replace('/', '.').replace('\\', '.')
            client.load_extension(f"data.{file[:-3]}")
    print('All commands loaded, boot successful')
    
# Everything is in the Data and Cogs only commands here are for loading and unloading those commands and the dev commands
# gonna add commands later
    
client.run(os.getenv('EVENTTOKEN'))