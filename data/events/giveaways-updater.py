import discord
import asyncio
from datetime import datetime, timedelta
from discord.ext import commands
from data.utils.functions import console_log

async def gmessage_update_loop(giveaway, remaining_time):
    while True:        
        if remaining_time.days > 0:
            await asyncio.sleep(60*60*12)
            to_deduct = timedelta(days=1)

        elif remaining_time.seconds > 60*60:
            await asyncio.sleep(60*60)
            to_deduct = timedelta(hours=1)

        elif remaining_time.seconds > 60:
            await asyncio.sleep(60)
            to_deduct = timedelta(minutes=1)

        elif remaining_time.seconds > 10:
            await asyncio.sleep(10)
            to_deduct = timedelta(seconds=10)
        else:
            for i in range(0, 10):
                await giveaway_message.edit(embed=discord.Embed(
                    title=giveaway_message.embed.title,
                    description=f'React on this message with :tada: to enter! This is you last chance!\nEnding in **{10-i} seconds**',
                    color=discord.Color.red(),
                    timestamp=giveaway_message.embed.timestamp
                ).set_footer(
                    text=giveaway_message.embed.footer.text
                ).set_author(
                    name=giveaway_message.embed.author.name,
                    icon_url=giveaway_message.embed.author.icon_url
                ))

            await self.client.get_channel(gchannel_id).send(f"")

        remaining_time -= to_deduct
        gchannel_id, gmessage_id = giveaway["id"].split("/")
        giveaway_message = await self.client.get_channel(gchannel_id).fetch_message(gmessage_id)
        await giveaway_message.edit(embed=discord.Embed(
            title=giveaway_message.embed.title,
            description=f'React on this message with :tada: to enter!\nGiveaway ends in {str(remaining_time)}',
            color=discord.Color.gold(),
            timestamp=giveaway_message.embed.timestamp
        ).set_footer(
            text=giveaway_message.embed.footer.text
        ).set_author(
            name=giveaway_message.embed.author.name,
            icon_url=giveaway_message.embed.author.icon_url
        ))
class Giveaways(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_ready(self):
        console_log("Loading all the giveaway messages\nthis can take a while...", "orange")
        await asyncio.sleep(3)
        for guild in self.client.guilds:
            try:
                giveaways = self.client.id_list["guild_setup_id_saves"][str(guild.id)]["giveaways"]
            except KeyError:
                continue
            for giveaway in giveaways
                start_on_json = giveaway["started_on"]
                started_on = datetime(
                    year=start_on_json["year"],
                    month=start_on_json["month"],
                    day=start_on_json["day"],
                    hour=start_on_json["hour"],
                    minute=start_on_json["minute"],
                    second=start_on_json['second']
                )
                giveaway_running_for = datetime.utcnow() - started_on
                how_long_to_run_json = giveaway["timestamps"]
                how_long_to_run = datetime(
                    year=how_long_to_run_json["year"],
                    month=how_long_to_run_json["month"],
                    day=how_long_to_run_json["day"],
                    hour=how_long_to_run_json["hour"],
                    minute=how_long_to_run_json["minute"],
                    second=how_long_to_run_json['second']
                )
                remaining_time = how_long_to_run - giveaway_running_for
                
                asyncio.create_task(gmessage_update_loop(giveaway, remaining_time))
