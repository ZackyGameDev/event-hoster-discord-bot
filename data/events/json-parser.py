import discord
import json

from discord.ext import commands, tasks

class JsonParser(commands.Cog):
    
    def __init__(self, client):    
        self.client = client
        self.save_data_as_json.start()
        
    def cog_unload(self):
        self.save_data_as_json.stop()
        
    @commands.Cog.listener()
    async def on_ready(self):
        try:
            json_data_file = open("id-list.json", "r")
        except IOError:
            json_data_file = open("id-list.json", "w+")
        json_data = json.load(json_data_file.read())
        self.client.id_list = json_data
        json_data_file.close()

    @tasks.loop(minutes=5)
    async def save_data_as_json(self):
        json_data_file = open("id_list.json", "w")
        json.dump(self.client.id_list, json_data_file, indent=4)
        
    @save_data_as_json.before_loop
    async def before_save_loop(self):
        print("Checking if the client is ready to start data.events.json-parser : tasks.loop")

def setup(client):
    client.add_cog(JsonParser(client))