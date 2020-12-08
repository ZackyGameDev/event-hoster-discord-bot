import discord
import json
import os

from discord.ext import commands
from data.utils.functions import console_log, read_file
from data.utils.checks import author_is_zacky


class DebugCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        console_log("Debug Commands are ACTIVE", "white", "on_blue")

    @commands.command()
    @commands.check(author_is_zacky)
    async def git_pull(self, ctx):
        os.system("git pull")

    @commands.command()
    @commands.check(author_is_zacky)
    async def debug_upload_json_to_discord(self, ctx):
        channel_to_upload_to = self.client.get_channel(json.loads(
            read_file("config.json"))["json_file_upload_channel_id"])
        console_log("Attempting to upload the json file to TC.{}({}) (requested through debug command)".format(
            channel_to_upload_to.name, channel_to_upload_to.id), "yellow")
        await ctx.send("Attempting to upload the json file to TC.{}({}) (requested through debug command)".format(channel_to_upload_to.name, channel_to_upload_to.id))
        try:
            await channel_to_upload_to.send(file=discord.File("id-list.json"))
            console_log("JSON file upload success", "green")
            await ctx.send("JSON file upload success")
        except Exception as e:
            console_log(f"Upload JSON failed: {e}", "red")
            await ctx.send(f"Upload JSON failed: {e}")

    @commands.command()
    @commands.check(author_is_zacky)
    async def debug_show_vars(self, ctx):
        try:
            await ctx.send(self.client.database)
        except Exception as e:
            await ctx.send(e)
        try:
            await ctx.send(self.client.id_list)
        except Exception as e:
            await ctx.send(e)

    # @commands.Cog.listener()
    # # I was having trouble getting it to detect reactions removes in data.commands.eventshosting.simonsays.simon_says_start() so i put this here to see if the bot even sees any reactions being removed
    # async def on_raw_reaction_remove(self, payload):
    #     console_log(f"Reaction removed: {str(payload)}")

    # @commands.Cog.listener()
    # async def on_raw_reaction_add(self, payload):
    #     console_log(f"Reaction added: {str(payload)}")

    # @commands.Cog.listener()
    # # I was having trouble getting it to detect reactions removes in data.commands.eventshosting.simonsays.simon_says_start() so i put this here to see if the bot even sees any reactions being removed
    # async def on_reaction_remove(self, reaction, user):
    #     console_log(f"Reaction removed: {reaction, user}")

    # @commands.Cog.listener()
    # async def on_reaction_add(self, reaction, user):
    #     console_log(f"Reaction added: {reaction, user}")


def setup(client):
    client.add_cog(DebugCommands(client))
