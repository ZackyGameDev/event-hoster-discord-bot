import discord
import os
from discord.ext import commands

client = commands.Bot(command_prefix=('z!', '.', '!', '>', '>>>', '-'), case_insensitive=True)

def author_is_zacky(ctx):
    return ctx.author.id == 625987962781433867

@client.event
async def on_ready():        
    # getting list of all paths to extensions
    filelist = []
    for root, dirs, files in os.walk("data/"):
        for file in files:
            filelist.append(os.path.join(root,file))

    # And then loading them
    blacklisted_extensions = [
        "data.events.database-fetcher",
        "data.commands.moderation"
    ]
    
    for file in filelist:
        if file.endswith('.py'):
            file = file.replace('/', '.').replace('\\', '.')[:-3]
            try:
                if file not in blacklisted_extensions:
                    client.load_extension(f"{file}")
                    print(f"Loaded extension: {file}")
                else:
                    print(f"Blacklisted extension not loaded: {file}")
            except Exception as e:
                print(f"Failed to load the extension: {file}, reason: {e}`")
    
    print('Commands and Extensions loaded, boot successful')
    
@client.command()
@commands.check(author_is_zacky)
async def reload_extension(ctx, extension):
    try:
        client.unload_extension(extension)
        client.load_extension(extension)
        msg = "Reloaded {} extension.".format(extension)
        print(msg)
        await ctx.send(msg)
    except Exception as e:
        await ctx.send(e)
        print("Extension Reload failed: {}".format(e))
        
@client.command()
@commands.check(author_is_zacky)
async def unload_extension(ctx, extension):
    try:
        client.unload_extension(extension)
        msg = "Unloaded {} extension".format(extension)
    except Exception as e:
        msg = "Failed to unload extension {}, {}".format(extension, e)
    
    print(msg)
    await ctx.send(msg)
    
@client.command()
@commands.check(author_is_zacky)
async def load_extension(ctx, extension):
    try:
        client.load_extension(extension)
        msg = "Loaded {} extension".format(extension)
    except Exception as e:
        msg = "Failed to load extension {}, {}".format(extension, e)
    
    print(msg)
    await ctx.send(msg)

# Everything is in the Data and Cogs only commands here are for loading and unloading those commands and the dev commands
# gonna add commands later

client.run(open("token.txt", "r").read())