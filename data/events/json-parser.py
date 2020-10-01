import discord
import json

from termcolor import cprint
from discord.ext import commands, tasks
from data.utils.functions import console_log, read_file

class JsonParser(commands.Cog):
    
    def __init__(self, client):    
        self.client = client
        self.save_data_as_json.start()
        self.upload_json_to_discord.start()
        
    def cog_unload(self):
        self.save_data_as_json.stop()
        self.upload_json_to_discord.stop()
        
    @commands.Cog.listener()
    async def on_ready(self):
        try:
            json_data_file = open("id-list.json", "r")
        except IOError:
            json_data_file = open("id-list.json", "w+")
        json_data = json.loads(json_data_file.read())
        self.client.id_list = json_data
        console_log(f'Loaded the json data: {json.dumps(self.client.id_list, indent=2, sort_keys=True)}', "green")
        json_data_file.close()

    @tasks.loop(minutes=2)
    async def save_data_as_json(self):
        json_data_file = open("id-list.json", "w")
        json.dump(self.client.id_list, json_data_file, indent=4)

    # I really wanted to have the json file stored on some other place, where i could access it from, in case the bot's hosting went down, so for now, im uploading it to a discord channel as a file, later I will have the data\events\database-fetcher.py do it        
    @tasks.loop(hours=6)
    async def upload_json_to_discord(self):
        channel_to_upload_to = self.client.get_channel(json.loads(read_file("config.json"))["json_file_upload_channel_id"])
        console_log("Attempting to upload the json file to TC.{}({})".format(channel_to_upload_to.name, channel_to_upload_to.id), "yellow")
        try:
            await channel_to_upload_to.send(file=discord.File("id-list.json"))
            console_log("JSON file upload success", "green")
        except Exception as e:
            console_log(f"Upload JSON failed: {e}", "red")
        
    @save_data_as_json.before_loop
    @upload_json_to_discord.before_loop
    async def before_save_loop(self):
        console_log("Checking if the client is ready to start data.events.json-parser : tasks.loop(s)", "white")
        await self.client.wait_until_ready()
        console_log("data.events.json-parser : tasks.loop(s) has been started!", "green")

def setup(client):
    client.add_cog(JsonParser(client))