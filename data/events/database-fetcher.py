import discord
import gspread
import asyncio
import os

from oauth2client.service_account import ServiceAccountCredentials
from discord.ext import commands, tasks
from urllib.request import urlopen
from data.utils.functions import console_log

# SOME VISUALIZATIONS
#  what the sheet looks like:
# +-----------+----------------------+----------------------+----------------------+-------------------------+
# | server_id | id_channel_simonsays | id_role_simonalive   |  id_role_simondead   | id_role_simoncontroller |
# +-----------+----------------------+----------------------+----------------------+-------------------------+
# | 123456789 | 12345678945435547564 | 12345678945435547564 | 12345678945435547564 |   12345678945435547564  |
# +-----------+----------------------+----------------------+----------------------+-------------------------+
# | 123456789 | 12345678945435547564 | 12345678945435547564 | 12345678945435547564 |   12345678945435547564  |
# +-----------+----------------------+----------------------+----------------------+-------------------------+
# | 123456789 | 12345678945435547564 | 12345678945435547564 | 12345678945435547564 |   12345678945435547564  |
# +-----------+----------------------+----------------------+----------------------+-------------------------+
# | 123456789 | 12345678945435547564 | 12345678945435547564 | 12345678945435547564 |   12345678945435547564  |
# +-----------+----------------------+----------------------+----------------------+-------------------------+
# | 123456789 | 12345678945435547564 | 12345678945435547564 | 12345678945435547564 |   12345678945435547564  |
# +-----------+----------------------+----------------------+----------------------+-------------------------+

# What <json>client.id_database looks like:
# {
#   "server_id" : {
#     'id_channel_simonsays': 1234,
#     'id_role_simonalive': 1234,
#     'id_role_simondead': 1234,
#     'id_role_simoncontroller': 1234
#   },
#   "server_id" : {
#     'id_channel_simonsays': 1234,
#     'id_role_simonalive': 1234,
#     'id_role_simondead': 1234,
#     'id_role_simoncontroller': 1234
#   }
# }


class DatabaseFetcher(commands.Cog):

    # Logging into google sheets here
    def __init__(self, client):
        scope = [
            "https://spreadsheets.google.com/feeds",
            'https://www.googleapis.com/auth/spreadsheets',
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive"
        ]

        creds = ServiceAccountCredentials.from_json_keyfile_name(
            "ServiceAccountCreds.json", scopes=scope)
        gspread_client = gspread.authorize(creds)
        # my google sheet was called api-tutorial then, idk why i didn't change it then, NOR AM I GOING TO CHANGE IT NOW, SIKE.
        sheet = gspread_client.open("api-tutorial").sheet1
        self.client = client
        self.sheet = sheet
        self.fetchdatabase.start()

    def cog_unload(self):
        self.fetchdatabase.stop()

    @commands.Cog.listener()
    async def on_ready(self):
        # Retrieving the database
        self.client.id_database = dict()
        # it will look something like [{'server_id': 3, 'id_channel_simonsays': 2, 'id_role_simonalive': 2, 'id_role_simondead': 3, 'id_role_simoncontroller': 4}, {'server_id': 3, 'id_channel_simonsays': 2, 'id_role_simonalive': 2, 'id_role_simondead': 5, 'id_role_simoncontroller': 32}]
        sheet_rows = self.sheet.get_all_records()
        for row in sheet_rows:
            row_items_in_list = [int(row[i]) for i in row]
            self.client.id_database[row_items_in_list[0]] = {
                'id_channel_simonsays': row_items_in_list[1],
                'id_role_simonalive': row_items_in_list[2],
                'id_role_simondead': row_items_in_list[3],
                'id_role_simoncontroller': row_items_in_list[4]
            }
        
        console_log(f'Loaded google sheet databaes: {self.client.id_database}', "green", have_to_pprint=True)

    @tasks.loop(minutes=15)
    async def fetchdatabase(self):
        console_log('Database fetch has started', "yellow")

        # Pushing the local data to the online database
        data_to_push = list()

        for server_id in self.client.id_database:
            data_to_push.append([
                str(server_id),
                str(self.client.id_database[server_id]['id_channel_simonsays']),
                str(self.client.id_database[server_id]['id_role_simonalive']),
                str(self.client.id_database[server_id]['id_role_simondead']),
                str(self.client.id_database[server_id]['id_role_simoncontroller'])
            ])
        
        self.sheet.delete_rows(2, len(self.sheet.get_all_records())+3)
        self.sheet.append_rows(data_to_push)
        
        console_log('Database Pushed to google sheet', "green")

    @fetchdatabase.before_loop
    async def before_fetch_loop(self):
        console_log(
            "Checking if the client is ready to start data.events.database-fetcher : tasks.loop", "blue")
        await self.client.wait_until_ready()


def setup(client):
    client.add_cog(DatabaseFetcher(client))
