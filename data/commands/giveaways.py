import discord
import asyncio
from discord.ext import commands
from random import random, randrange
from datetime import datetime, timedelta
from data.events.giveawaysupdater import gmessage_update_loop


class Giveaways(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.group(pass_context=True)
    async def giveaway(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(
                embed=discord.Embed(
                    title='Invalid giveaway command passed!',
                    description='If you would like to get a full list of commands then please use the help command.',
                    color=discord.Color.red()
                )
            )

    @giveaway.command()
    async def start(self, ctx):

        has_giveaway_perms = False
        for role in ctx.author.roles:
            if role.name.lower() == "giveaways":
                has_giveaway_perms = True

        if ctx.author.permissions_in(ctx.channel).manage_guild:
            has_giveaway_perms = True

        if not has_giveaway_perms:
            await ctx.send(embed=discord.Embed(
                title="Missing Permissions!",
                description="You either need the `manage server` permission or have a role named Giveaways to perform this action!",
                color=discord.Color.red()
            ))
            return

        def is_reply(message: discord.Message):
            return ctx.channel == message.channel and ctx.author == message.author

        cancelled_embed = discord.Embed(
            title='Stopped',
            description="Giveaway creation has been cancelled",
            color=discord.Color.red()
        )

        # How long will it last?
        await ctx.send(embed=discord.Embed(
            description='Please tell me how long this giveaway will last\n\n`For e.g. if you want this to last 1 day 2 hours and 4 minutes, reply like this: 1d 2h 4m`',
            color=discord.Color.from_hsv(random(), 1, 1)
        ).set_footer(
            text="You can cancel this by typing `stop`"
        ))

        time_stamps = {
            "days": 0,
            "hours": 0,
            "minutes": 0,
            "seconds": 0
        }

        message = await self.client.wait_for('message', check=is_reply, timeout=60)
        if message.content.lower() == "stop":
            await ctx.send(embed=cancelled_embed)
            return

        time_stamps_input = message.content.split(' ')
        set_time = ""

        for time_stamp in time_stamps_input:
            for unit in time_stamps:
                if time_stamp.endswith(unit[0]):
                    time_stamps[unit] = int(time_stamp[:-1])
                    set_time = set_time + \
                        time_stamp[:-1]+' '+unit.capitalize()+' '

        if set_time != "":
            await ctx.send(embed=discord.Embed(title="Alright!", description=f"Alright! The Giveaway will last **{set_time}**", color=discord.Color.gold()))
        else:
            await ctx.send(embed=discord.Embed(title="Failed", description=f'The time stamp you gave couldn\'t be recognised, make sure you are using the correct format!', color=discord.Color.red()))
            return

        # how many Winners will it have?
        await ctx.send(embed=discord.Embed(
            description='Please tell me What the prize of this giveaway will be',
            color=discord.Color.from_hsv(random(), 1, 1)
        ).set_footer(
            text="You can cancel this by typing `stop`"
        ))

        message = await self.client.wait_for('message', check=is_reply, timeout=60)
        if message.content.lower() == "stop":
            await ctx.send(embed=cancelled_embed)
            return
        elif len(message.content) > 240:
            await ctx.send(embed=discord.Embed(description="The prize can only be 240 characters long!", color=discord.Color.red()))
            return
        else:
            prize = message.content
        await ctx.send(embed=discord.Embed(title="Understood", description=f'This giveaway will have {prize} as prize', color=discord.Color.from_hsv(random(), 1, 1)))

        # What will be given away?
        await ctx.send(embed=discord.Embed(
            description='Please tell me how many winners this giveaway will have\n\n`Maximum number is 10`',
            color=discord.Color.from_hsv(random(), 1, 1)
        ).set_footer(
            text="You can cancel this by typing `stop`"
        ))

        message = await self.client.wait_for('message', check=is_reply, timeout=60)
        if message.content.lower() == "stop":
            await ctx.send(embed=cancelled_embed)
            return
        winners = int(message.content)
        if winners > 10:
            await ctx.send(embed=discord.Embed(description="Winners cannot be more than **10**", color=discord.Color.red()))
            return
        await ctx.send(embed=discord.Embed(title="Understood", description=f'This giveaway will have {winners} winners', color=discord.Color.from_hsv(random(), 1, 1)))

        # In which channel!?!?
        await ctx.send(embed=discord.Embed(
            description="Please tell me in which channel will this giveaway be created",
            color=discord.Color.from_hsv(random(), 1, 1)
        ).set_footer(
            text="You can cancel this by typing `stop`"
        ))

        message = await self.client.wait_for('message', check=is_reply, timeout=60)
        if message.content.lower() == "stop":
            await ctx.send(embed=cancelled_embed)
            return
        channel = ctx.guild.get_channel(int(message.content[:-1][-18:]))
        await ctx.send(embed=discord.Embed(title="Understood", description=f'This giveaway will be hosted in <#{channel.id}>', color=discord.Color.from_hsv(random(), 1, 1)))

        # All set?
        confirm_msg = await ctx.send(embed=discord.Embed(
            title="All set?",
            description="Proceed?",
            color=discord.Color.from_hsv(random(), 1, 1)
        ).set_footer(
            text="React on this message to confirm"
        ))

        await confirm_msg.add_reaction("✅")
        await confirm_msg.add_reaction("❎")

        def check(reaction, user, confirm_msg=confirm_msg):
            return user == ctx.message.author and reaction.message.id == confirm_msg.id and str(reaction.emoji) in ("✅", "❎")

        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout=600, check=check)
        except asyncio.TimeoutError:
            await confirm_msg.edit(embed=discord.Embed(
                title="Failed!",
                description="You took too much time to react!",
                color=discord.Color.red()
            ).set_footer(
                text="Try again"
            ))

        if reaction.emoji == "❎":
            await confirm_msg.edit(embed=discord.Embed(
                title="Cancelled",
                description="You cancelled the creation of the giveaway",
                color=discord.Color.red()
            ))
            return

        giveaway_message = await channel.send(embed=discord.Embed(
            title=f"{winners} {prize} Giveaway!",
            description=f"React on this message with :tada: to enter!\nGiveaway Ends in: **{set_time}**",
            timestamp=datetime.utcnow() +
            timedelta(days=time_stamps['days'], seconds=time_stamps['seconds'],
                      minutes=time_stamps['minutes'], hours=time_stamps['hours']),
            color=discord.Color.from_rgb(
                0, randrange(0, 255), randrange(0, 255))
        ).set_author(
            name=f'{ctx.author}',
            icon_url=f'https://cdn.discordapp.com/avatars/{ctx.author.id}/{ctx.author.avatar}.png'
        ).set_footer(
            text="This Giveaway will end on "
        ))

        await giveaway_message.add_reaction("🎉")

        started_on = {
            "year": datetime.now().year,
            "month": datetime.now().month,
            "day": datetime.now().day,
            "hour": datetime.now().hour,
            "minute": datetime.now().minute,
            "second": datetime.now().second
        }

        giveaway = {
            "started_on": started_on,
            "timestamps": time_stamps,
            "winners": winners,
            "prize": prize,
            "id": f"{channel.id}/{giveaway_message.id}"
        }

        try:
            self.client.id_list['guild_setup_id_saves'][str(
                ctx.guild.id)]["giveaways"].append(giveaway)
        except KeyError:
            try:
                self.client.id_list['guild_setup_id_saves'][str(ctx.guild.id)]["giveaways"] = [
                    giveaway]
            except KeyError:
                self.client.id_list['guild_setup_id_saves'][str(ctx.guild.id)] = {
                    "giveaways": [giveaway]}

        # Start updating the giveaway message
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

        await ctx.send(embed=discord.Embed(
            title="Giveaway started!",
            description=f"Giveaway started in <#{channel.id}>",
            color=discord.Color.green()
        ))


def setup(client):
    client.add_cog(Giveaways(client))
