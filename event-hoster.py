import discord
import os
import json
import time
import colorama
import sys

from discord.ext.commands.errors import NoEntryPointError
from data.custom.checks import author_is_zacky
from data.custom.functions import read_file, console_log, cprint
from discord.ext import commands

client = commands.Bot(command_prefix=('z!', '.', '!', '>', '>>>', '-'), case_insensitive=True)
client.version = "v0.0.4"
client.id_list = {}
colorama.init()

def boot_bot(blacklisted_extensions : tuple) -> None: # i am not using the on_ready event because then the on_ready event in cogs won't work, and putting it all in a function so its looking clean
    # unecessary decoration (i like it please don't attack me)
    if sys.platform == "win32" or sys.platform == "win64":
        os.system("cls")
    else:
        os.system("clear")
    cprint(read_file("startup_ascii.txt").format(client.version), "yellow")
    
    # getting list of all paths to extensions
    filelist = []
    for root, dirs, files in os.walk("data/"):
        for file in files:
            filelist.append(os.path.join(root,file))

    # And then loading them    
    for file in filelist:
        if file.endswith('.py'):
            file = file.replace('/', '.').replace('\\', '.')[:-3]
            try:
                if file not in blacklisted_extensions:
                    client.load_extension(f"{file}")
                    console_log(f"Loaded extension: {file}", "yellow")
                else:
                    console_log(f"Blacklisted extension not loaded: {file}", "red")
            except NoEntryPointError:
                console_log(f"{file} has no entry point, assuming that its not an extension.", "blue")
            except Exception as e:
                console_log(f"Failed to load the extension: {file}, reason: {sys.exc_info()[0]}, {e}`", "white", "on_red")


boot_bot(blacklisted_extensions = json.loads(read_file("config.json"))["blacklisted_extensions"])
@client.event
async def on_ready():              
    console_log('~~~~~~ Commands and Extensions loaded, boot successful ~~~~~~', "green")
    console_log("~~~~~~~~ Below are the messages from the extensions ~~~~~~~~~", "cyan")
    
@client.command()
@commands.check(author_is_zacky)
async def reload_extension(ctx, extension):
    try:
        client.unload_extension(extension)
        client.load_extension(extension)
        msg = "Reloaded {} extension.".format(extension)
        console_log(msg, "yellow")
        await ctx.send(msg)
    except Exception as e:
        await ctx.send(e)
        console_log("Extension Reload failed: {}".format(e), "white", "on_red")
        
@client.command()
@commands.check(author_is_zacky)
async def unload_extension(ctx, extension):
    try:
        client.unload_extension(extension)
        msg = "Unloaded {} extension".format(extension)
        col = "yellow"
        on_col = None
    except Exception as e:
        msg = "Failed to unload extension {}, {}".format(extension, e)
        col = 'white'
        on_col = 'on_red'
    
    console_log(msg, col, on_col)
    await ctx.send(msg)
    
@client.command()
@commands.check(author_is_zacky)
async def load_extension(ctx, extension):
    try:
        client.load_extension(extension)
        msg = "Loaded {} extension".format(extension)
        col = "yellow"
        on_col = None
    except Exception as e:
        msg = "Failed to load extension {}, {}".format(extension, e)
        col = 'white'
        on_col = 'on_red'

    console_log(msg, col, on_col)
    await ctx.send(msg)

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass   # I know that these errors are automatically ignored, but the error messages might start flooding the console, which is, uhh, a big no no
    else:
        raise error # because i don't want it to not raise any other errors

# Everything is in the Data and Cogs only commands here are for loading and unloading those commands and the dev commands
# gonna add commands later

client.run(read_file("token.txt"))
