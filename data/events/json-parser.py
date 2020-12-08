import discord
import json

from termcolor import cprint
from discord.ext import commands, tasks
from data.utils.functions import console_log, read_file

initial_json = {  # If the json file doesn't exist, i will create it and put this data into it
    "emojis": {
        "checkGif": "<a:checkGif:760758712876400680>",
        "crossGif": "<a:crossGif:760758713777913876>"
    },
    "tickets_count": {},
    "prefixes": {},
    "guild_setup_id_saves": {},
    "important_users": {
        "Zacky": 625987962781433867
    }
}


class JsonParser(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.save_data_as_json.start()
        self.upload_json_to_discord.start()
        try:
            read_file('id-list.json')
        except:
            f = open('id-list.json', 'w')
            f.write(json.dumps(initial_json))
            f.close()

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
        self.client.id_list: dict = json_data
        console_log(
            f'Loaded the json data: {json.dumps(self.client.id_list, indent=2, sort_keys=True)}', "green")
        json_data_file.close()
        self.client.id_list['emojis'] = initial_json['emojis']

    @tasks.loop(seconds=30)
    async def save_data_as_json(self):
        json_data_file = open("id-list.json", "w")
        json.dump(self.client.id_list, json_data_file, indent=4)

    # I really wanted to have the json file stored on some other place, where i could access it from, in case the bot's hosting went down, so for now, im uploading it to a discord channel as a file, later I will have the data\events\database-fetcher.py do it
    @tasks.loop(minutes=60)
    # I fisrt used to upload the whole thing as a file, but that's actually the worst thing to o because that can get this rate limited real quick, so i'm make it send it in a message instead
    async def upload_json_to_discord(self):
        channel_to_upload_to = self.client.get_channel(json.loads(
            read_file("config.json"))["json_file_upload_channel_id"])
        console_log("Attempting to upload, or send the json file data to TC:{}({})".format(
            channel_to_upload_to.name, channel_to_upload_to.id), "yellow")
        try:
            # await channel_to_upload_to.send(file=discord.File("id-list.json"))
            json_to_send = ""
            for i in read_file("id-list.json"):
                json_to_send = json_to_send + i
                # Send message limit is 2000, keeping it to 1900 just to be on the safe side
                if len(json_to_send) > 1900:
                    await channel_to_upload_to.send(f"```json\n{json_to_send}```")
                    json_to_send = ""
            await channel_to_upload_to.send(f"```json\n{json_to_send}```")

            console_log("JSON file data sent", "green")
        except Exception as e:
            console_log(f"Upload JSON data failed: {e}", "red")

    @save_data_as_json.before_loop
    @upload_json_to_discord.before_loop
    async def before_save_loop(self):
        console_log(
            "Checking if the client is ready to start data.events.json-parser : tasks.loop(s)", "white")
        await self.client.wait_until_ready()
        console_log(
            "data.events.json-parser : tasks.loop(s) has been started!", "green")


def setup(client):
    client.add_cog(JsonParser(client))
