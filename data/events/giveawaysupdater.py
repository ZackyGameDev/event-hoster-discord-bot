import discord
import asyncio
import random
from datetime import datetime, timedelta
from discord.ext import commands
from data.utils.functions import console_log


async def gmessage_update_loop(self, giveaway, remaining_time):
    while True:
        if remaining_time.days <= -1:
            # If event hoster missed the ending of the giveaway, (perhaps because of downtime), set the time to end in 10 seconds
            remaining_time = timedelta(seconds=10)
            to_deduct = timedelta(seconds=0)

        elif remaining_time.days >= 30:
            await asyncio.sleep(60*60*12*7*30)
            to_deduct = timedelta(days=30)

        elif remaining_time.days >= 7:
            await asyncio.sleep(60*60*12*7)
            to_deduct = timedelta(days=7)

        elif remaining_time.days >= 1:
            await asyncio.sleep(60*60*12)
            to_deduct = timedelta(days=1)

        elif remaining_time.seconds >= 60*60:
            await asyncio.sleep(60*60)
            to_deduct = timedelta(hours=1)

        elif remaining_time.seconds >= 60:
            await asyncio.sleep(60)
            to_deduct = timedelta(minutes=1)

        elif remaining_time.seconds >= 10:
            await asyncio.sleep(10)
            to_deduct = timedelta(seconds=10)

        else:
            # Last ten seconds!
            for i in range(0, 10):
                await asyncio.sleep(1)

                gchannel_id, gmessage_id = map(int, giveaway["id"].split("/"))
                giveaway_message = await self.client.get_channel(gchannel_id).fetch_message(gmessage_id)
                await giveaway_message.edit(embed=discord.Embed(  # Giveaway message will be defined on the first run of this loop
                    title=giveaway_message.embeds[0].title,
                    description=f'React on this message with :tada: to enter! This is you last chance!\nEnding in **{10-i} seconds**',
                    color=discord.Color.red(),
                    timestamp=giveaway_message.embeds[0].timestamp
                ).set_footer(
                    text=giveaway_message.embeds[0].footer.text
                ).set_author(
                    name=giveaway_message.embeds[0].author.name,
                    icon_url=giveaway_message.embeds[0].author.icon_url
                ))
            for reaction in giveaway_message.reactions:
                if str(reaction.emoji) == "🎉":
                    users = await reaction.users().flatten()
                    # users is now a list of User...

            # If no reaction, set users to a single item list so it is defined for later
            try:
                users
            except NameError:
                users = [1]

            # If not enough people participated
            if len(users)-1 < giveaway['winners']:
                await giveaway_message.channel.send(f"Not enough participants to declare winner! hence it's a draw! Nobody won!\nhttps://discordapp.com/channels/{giveaway_message.channel.guild.id}/{gchannel_id}/{gmessage_id}")
                await giveaway_message.edit(embed=discord.Embed(
                    title="Giveaway ended!",
                    description=f"Prize: {giveaway['prize']}\nWinner(s): Nobody!",
                    color=discord.Color.red(),
                    timestamp=giveaway_message.embeds[0].timestamp
                ).set_footer(
                    text="Giveaway ended on"
                ).set_author(
                    name=giveaway_message.embeds[0].author.name,
                    icon_url=giveaway_message.embeds[0].author.icon_url
                ))
                self.client.id_list["guild_setup_id_saves"][str(
                    giveaway_message.guild.id)]["giveaways"].remove(giveaway)
                return

            # Declaring a winner
            winners = str()
            for i in range(giveaway["winners"]):
                winner = f"<@{random.choice(users).id}>"
                while winner == f"<@{self.client.user.id}>": # I don't want the bot to congratulate itself
                    winner = f"<@{random.choice(users).id}>"
                winners = winners + winner + ' '
                await giveaway_message.channel.send(f"Congratulations {winner}! You won **{giveaway['prize']}**\nhttps://discordapp.com/channels/{giveaway_message.channel.guild.id}/{gchannel_id}/{gmessage_id}")
            await giveaway_message.edit(embed=discord.Embed(
                title="Giveaway ended!",
                description=f"Prize: {giveaway['prize']}\nWinner(s): {winners}",
                color=discord.Color.gold(),
                timestamp=giveaway_message.embeds[0].timestamp
            ).set_footer(
                text="Giveaway ended on"
            ).set_author(
                name=giveaway_message.embeds[0].author.name,
                icon_url=giveaway_message.embeds[0].author.icon_url
            ))

            self.client.id_list["guild_setup_id_saves"][str(
                giveaway_message.guild.id)]["giveaways"].remove(giveaway)
            return

        remaining_time -= to_deduct
        gchannel_id, gmessage_id = map(int, giveaway["id"].split("/"))
        giveaway_message = await self.client.get_channel(gchannel_id).fetch_message(gmessage_id)
        await giveaway_message.edit(embed=discord.Embed(
            title=giveaway_message.embeds[0].title,
            description=f'React on this message with :tada: to enter!\nGiveaway ends in {str(remaining_time)}',
            color=discord.Color.gold(),
            timestamp=giveaway_message.embeds[0].timestamp
        ).set_footer(
            text=giveaway_message.embeds[0].footer.text
        ).set_author(
            name=giveaway_message.embeds[0].author.name,
            icon_url=giveaway_message.embeds[0].author.icon_url
        ))


class GiveawaysUpdater(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        console_log(
            "Loading all the giveaway messages\nthis can take a while...", "yellow")
        await asyncio.sleep(3)
        for guild in self.client.guilds:
            try:
                giveaways = self.client.id_list["guild_setup_id_saves"][str(
                    guild.id)]["giveaways"]
            except KeyError:
                continue
            for giveaway in giveaways:
                start_on_json = giveaway["started_on"]
                started_on = datetime(
                    year=start_on_json["year"],
                    month=start_on_json["month"],
                    day=start_on_json["day"],
                    hour=start_on_json["hour"],
                    minute=start_on_json["minute"],
                    second=start_on_json['second']
                )
                giveaway_running_for = datetime.now() - started_on
                how_long_to_run_json = giveaway["timestamps"]
                how_long_to_run = timedelta(
                    days=how_long_to_run_json["days"],
                    hours=how_long_to_run_json["hours"],
                    minutes=how_long_to_run_json["minutes"],
                    seconds=how_long_to_run_json['seconds']
                )
                remaining_time = how_long_to_run - giveaway_running_for

                asyncio.create_task(gmessage_update_loop(
                    self, giveaway, remaining_time))

        console_log("Loaded all the giveaway messages!", "green")


def setup(client):
    client.add_cog(GiveawaysUpdater(client))
