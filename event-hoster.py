import discord
import os
import json
import time
import colorama
import asyncio
import sys

from discord.ext.commands.errors import NoEntryPointError
from data.utils.checks import author_is_zacky
from data.utils.functions import read_file, console_log, cprint
from discord.ext import commands, tasks


def get_guild_prefix(client: commands.Bot, message: discord.Message):
    try:
        return client.id_list['prefixes'][f'{message.guild.id}']
    except KeyError:
        client.id_list['prefixes'][f'{message.guild.id}'] = client.default_prefix
        # The client.prefix = get_guild_prefix, this is to avoid getting not defined function issue in cogs
        client.prefix(client, message)


intents: discord.Intents = discord.Intents.all()
client = commands.Bot(command_prefix=get_guild_prefix,
                      case_insensitive=True, intents=intents)
client.version = "v0.0.8"
client.id_list = {}
# If no custom prefixes for any guild is set, this is the prefix used by default
client.default_prefix = '$'
client.prefix = get_guild_prefix
colorama.init()


# i am not using the on_ready event because then the on_ready event in cogs won't work, and putting it all in a function so its looking clean
def boot_bot(blacklisted_extensions: tuple) -> None:
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
            filelist.append(os.path.join(root, file))

    # And then loading them
    lines = 0  # this is just a small thing i did for counting the lines of code written
    for file in filelist:
        if file.endswith('.py'):
            file = file.replace('/', '.').replace('\\', '.')[:-3]
            try:
                if file not in blacklisted_extensions:
                    client.load_extension(f"{file}")
                    console_log(f"Loaded extension: {file}", "yellow")
                else:
                    console_log(
                        f"Blacklisted extension not loaded: {file}", "red")
            except NoEntryPointError:
                console_log(
                    f"{file} has no entry point, assuming that its not an extension.", "blue")
            except Exception as e:
                console_log(
                    f"Failed to load the extension: {file}, reason: {sys.exc_info()[0]}, {e}`", "white", "on_red")


boot_bot(blacklisted_extensions=json.loads(
    read_file("config.json"))["blacklisted_extensions"])


@client.event
async def on_ready():
    # Gotta wait for the extensions to do their thing first, (for e.g. id_list needs to be defined)
    await asyncio.sleep(5)
    # Making sure every server has a default prefix to avoid future errors
    try:
        client.id_list['prefixes']
    except KeyError:
        client.id_list['prefixes'] = dict()
    console_log("Serving in the following guilds:")
    for guild in client.guilds:
        console_log(f"....{guild.name}[{guild.id}]")
        try:
            client.id_list['prefixes'][f'{guild.id}']
        except KeyError:
            client.id_list['prefixes'][f'{guild.id}'] = client.default_prefix

    console_log(
        '~~~~~~ Commands, Prefixes and Extensions loaded, boot successful ~~~~~~', "green")
    console_log('~~~~~~~~~~~ Serving in {} Number of guilds ~~~~~~~~~~~'.format(
        len(client.guilds)), "green")
    change_the_status.start()


@client.event
async def on_guild_join(guild: discord.Guild):
    console_log("I was added to the Server: %s, Owner of the server: %s :D" % (
        guild.name, guild.owner), "green")
    client.id_list['prefixes'][f'{guild.id}'] = client.default_prefix


@client.event
async def on_guild_remove(guild: discord.Guild):
    console_log("I was removed from the Server: %s, Owner of the server: %s" % (
        guild.name, guild.owner), "red")
    del client.id_list['prefixes'][f'{guild.id}']


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
        # because i don't want it to not raise any other errors
        console_log(str(error), "white", "on_red")


@tasks.loop(seconds=30)
async def change_the_status():
    game = discord.Game(
        f"on {len(client.guilds)} Discord servers [@me for help!]")
    await client.change_presence(status=discord.Status.online, activity=game)


@client.command()
async def ping(ctx):
    start = time.perf_counter()
    message = await ctx.send(embed=discord.Embed(
        description="Calculating Ping...",
        color=discord.Color.red()
    ))
    end = time.perf_counter()
    duration = (end - start) * 1000
    await message.edit(embed=discord.Embed(
        title='Response Delay: {:.2f}ms'.format(
            duration) + f"\nWebsocket Latency: {round(client.latency*1000)}ms",
        color=discord.Color.green()
    ))


@client.event
async def on_message(message: discord.Message):
    if isinstance(message.channel, discord.DMChannel):
        console_log(f'{message.author} messaged me: {message.content}')
        return
    if message.content in (f'<@{client.user.id}>', f'<@!{client.user.id}>'):
        await message.channel.send(f'**\n*My Prefix for this Server is `$p$`, use `$p$prefix` command to set a prefix for this server, and use `$p$help` to get a list of all the commands***'.replace('$p$', client.prefix(client, message)))

    await client.process_commands(message)


@client.command()
@commands.has_permissions(manage_guild=True)
async def prefix(ctx: commands.Context, prefix: str):
    client.id_list['prefixes'][f'{ctx.guild.id}'] = prefix
    await ctx.send(embed=discord.Embed(
        description="Prefix changed to `%s` Successfully" % (prefix, ),
        color=discord.Color.green()
    ))


@prefix.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("**\n:warning:** **You either don't have the `Manage Server` or I don't have the `Embed Links` permission** :warning:")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("**\n:warning:** **You didn't specify which prefix to set to!** :warning:\n***`For e.g. $p$prefix $`***".replace('$p$', client.prefix(client, ctx.message)))


@client.command()
async def report(ctx, *, to_report):
    await ctx.send(embed=discord.Embed(
        title="Bug Reported",
        description=f'The bug has been reported to my creator, which says:```{to_report}```',
        color=discord.Color.green()
    ).set_footer(
        text="Thank you for reporting and making me a better bot"
    ))

    await client.get_channel(json.loads(read_file("config.json"))["bug_reports_channel_id"]).send(embed=discord.Embed(
        title=f"Bug Report",
        description=f"```{to_report}```",
        color=discord.Color.red()
    ).set_author(
        name=f'{ctx.author}',
        icon_url=f'https://cdn.discordapp.com/avatars/{ctx.author.id}/{ctx.author.avatar}.png'
    ))


@client.command()
async def botinfo(ctx):
    await ctx.send(embed=discord.Embed(
        title="Bot info",
        description=json.loads(read_file("config.json"))[
            "bot_info"].replace("$p$", client.prefix()),
        color=discord.Color.gold()
    ).set_author(
        name=f'{ctx.author}',
        icon_url=f'https://cdn.discordapp.com/avatars/{ctx.author.id}/{ctx.author.avatar}.png'
    ))


@client.command()
async def invite(ctx):
    embed = discord.Embed(
        description="[Add me to your server!](https://discord.com/api/oauth2/authorize?client_id=759290479069626418&permissions=2147483639&scope=bot) \n[Join our discord Server!](https://discord.gg/QNsmC84)", color=0xfff700)
    embed.set_author(name="Event Hoster",
                     icon_url="https://cdn.discordapp.com/avatars/759290479069626418/f2b8ccbef278dcf0d03c3cd0d3b71b12.png")
    await ctx.send(embed=embed)


@client.command()
async def suggest(ctx, *, to_suggest):
    await ctx.send(embed=discord.Embed(
        title="Suggestion submitted",
        description=f'The suggestion has been submitted to my creator, which says:```{to_suggest}```',
        color=discord.Color.green()
    ).set_footer(
        text="Thank you for reporting and making me a better bot"
    ))

    await client.get_channel(json.loads(read_file("config.json"))["suggestions_channel_id"]).send(embed=discord.Embed(
        title=f"Suggestion",
        description=f"```{to_suggest}```",
        color=discord.Color.green()
    ).set_author(
        name=f'{ctx.author}',
        icon_url=f'https://cdn.discordapp.com/avatars/{ctx.author.id}/{ctx.author.avatar}.png'
    ))

client.run(read_file("token.txt"))
