import discord
import json
from discord.ext import commands
from data.utils.functions import get_role_from_msg, prettify_string, console_log, read_file, suffixed_time_to_int
from asyncio import TimeoutError
from random import random
from datetime import datetime, timedelta
import asyncio


async def edit_participation_embed(self, message: discord.Message, stop_after: int):
    await asyncio.sleep(stop_after)
    await message.edit(embed=discord.Embed(
        title="No longer Accepting Participants!",
        description=f"Reacting on this message will no longer accept you as Simon Says participant!",
        timestamp=message.embeds[0].timestamp,
        color=discord.Color.red()
    ).set_author(
        name=message.embeds[0].author.name,
        icon_url=message.embeds[0].author.icon_url
    ).set_footer(
        text=f"Was Accepting Participants Till"
    ))


async def get_simon_says_roles(self, ctx):
    try:
        simon_participant_role_id = self.client.id_list['guild_setup_id_saves'][str(
            ctx.guild.id)]['simon_says']['roles']['simon_says_participant']
        simon_disqualified_role_id = self.client.id_list['guild_setup_id_saves'][str(
            ctx.guild.id)]['simon_says']['roles']['simon_says_disqualified']
        simon_controller_role_id = self.client.id_list['guild_setup_id_saves'][str(
            ctx.guild.id)]['simon_says']['roles']['simon_says_controller']

        return simon_participant_role_id, simon_disqualified_role_id, simon_controller_role_id
    except KeyError:  # this error handling took a total of 6 hours to figure out
        await ctx.send(embed=discord.Embed(
            title=f"{self.emojis['crossGif']} Failed",
            description=f"You have not yet setup this server by using the `-SimonSaysSetup` command to do that!",
            color=discord.Color.red()
        ).set_footer(
            text="If you think this is an error, contact Zacky#9543"
        ))


class SimonSays(commands.Cog):
    def __init__(self, client):
        self.client: commands.Bot = client
        self.emojis = json.loads(read_file('id-list.json'))['emojis']

    @commands.command(aliases=["SimonSaysParticipationMessage", "SimonSaysStart"])
    @commands.bot_has_permissions(manage_roles=True)
    async def simon_says_start(self, ctx: commands.Context, *, stop_after: str):
        simon_participant_role_id, simon_disqualified_role_id, simon_controller_role_id = await get_simon_says_roles(self, ctx)
        simon_participant_role: discord.Role = ctx.guild.get_role(
            simon_participant_role_id)
        simon_controller_role: discord.Role = ctx.guild.get_role(
            simon_controller_role_id)

        if not simon_controller_role in ctx.author.roles:
            await ctx.send(embed=discord.Embed(description=f"You need to have the {simon_controller_role} Role to do that in this Server!", color=discord.Embed.red()))
            return

        # Converting `stop_after` to seconds
        try:
            original_stop_after_arg = stop_after.lower()
            stop_after = suffixed_time_to_int(stop_after.lower())
        except ValueError:
            await ctx.send(embed=discord.Embed(description="You can only add either of `s`, `m`, `h` after your number to represent the hours minutes and seconds respectively, after which this message will not accept participants. nothing else.", color=discord.Colour.red()))
            return

        if stop_after > 24 * 60 * 60:
            await ctx.send(embed=discord.Embed(description="That time is longer than a day!", color=discord.Colour.red()))
            return

        # Sending the participation message
        try:
            await ctx.message.delete()
        except:
            pass

        try:
            participation_message = await ctx.send(embed=discord.Embed(
                title="Simon Says Participation!",
                description=f"React on this message with :tada: to participate for simon says! This message will not accept participants {original_stop_after_arg.replace('s', ' Second(s)').replace('h', ' Hour(s)').replace('m', ' Minute(s)')} after this message was sent! participate quickly!",
                timestamp=datetime.utcnow() + timedelta(seconds=stop_after),
                color=discord.Color.from_hsv(random(), 1, 1)
            ).set_author(
                name=f'{ctx.author}',
                icon_url=f'https://cdn.discordapp.com/avatars/{ctx.author.id}/{ctx.author.avatar}.png'
            ).set_footer(
                text=f"Accepting Participants Till"
            ))
            asyncio.create_task(edit_participation_embed(
                self, participation_message, stop_after=stop_after))
        except:
            await ctx.send("***I Need the Embed Links permissions for this!***")
            return

        # Listening for reactions
        await participation_message.add_reaction("🎉")

        async def remove_participants_loop(timeout=stop_after*60):
            while True:
                try:
                    # the normal reaction_remove requires the message to be cached, to not have to deal with that, i am using raw_reaction_remove instead
                    payload: discord.RawReactionActionEvent = await self.client.wait_for('raw_reaction_remove', timeout=timeout, check=lambda payload: str(payload.emoji) == "🎉" and payload.message_id == participation_message.id and not "Reacting on this message will no longer accept you as Simon Says participant" in participation_message.embeds[0].description)
                    user: discord.Member = self.client.get_guild(
                        payload.guild_id).get_member(payload.user_id)
                    try:
                        await user.remove_roles(simon_participant_role)
                    except Exception as e:
                        console_log("Error in removing participant role from user: {}".format(
                            e), "white", "on_red")
                except TimeoutError:
                    break

        async def add_participants_loop(timeout=stop_after*60):
            while True:
                try:
                    reaction, user = await self.client.wait_for('reaction_add', timeout=timeout, check=lambda reaction, user: str(reaction.emoji) == "🎉" and reaction.message.id == participation_message.id and not "Reacting on this message will no longer accept you as Simon Says participant" in reaction.message.embeds[0].description)
                    try:
                        await user.add_roles(simon_participant_role)
                    except Exception as e:
                        console_log("Error in adding participant role to user: {}".format(
                            e), "white", "on_red")
                except TimeoutError:
                    break

        asyncio.create_task(add_participants_loop())
        asyncio.create_task(remove_participants_loop())

    @simon_says_start.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send("I lack the manage roles permission for this!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"<@{ctx.author.id}>, listen buddy, you also need to specify how many minutes to wait to delete the participation message, you don't won't participants in middle of your event, do you?")
        else:
            console_log(
                f"error in SimonSays.simon_says_start! {error}", "white", "on_red")

    @commands.command(aliases=['SimonSays', 'Simon-Says', 'ss'])
    async def simon_says(self, ctx, *, to_say):
        simon_participant_role_id, simon_disqualified_role_id, simon_controller_role_id = await get_simon_says_roles(self, ctx)

        if ctx.guild.get_role(simon_controller_role_id) not in ctx.author.roles:
            await ctx.send(embed=discord.Embed(
                title=f'{self.emojis["crossGif"]} Missing Permissions!',
                description=f"You don\'t have the <@&{simon_controller_role_id}> role to perform this command! {self.emojis['crossGif']}",
                color=discord.Color.red()
            ))
            return

        simon_says_channel = self.client.get_channel(self.client.id_list['guild_setup_id_saves'][str(
            ctx.guild.id)]["simon_says"]['channels']['simon_says_channel'])
        await simon_says_channel.send(embed=discord.Embed(
            title=f"Simon Says!",
            description=f"{to_say}",
            color=discord.Color.from_hsv(random(), 1, 1)
        ).set_author(
            name=f'{ctx.author}',
            icon_url=f'https://cdn.discordapp.com/avatars/{ctx.author.id}/{ctx.author.avatar}.png'
        ))

        if ctx.channel.id != simon_says_channel.id:
            await ctx.send(f"Said this message in <#{simon_says_channel.id}>!", delete_after=30)

        await ctx.message.delete()

    @commands.command(aliases=["simonRemaining", "SimonRemainingParticipants", "simonRemainingContestents", "simonRemainingAlive", "simonLeft", "simonleftalive"])
    async def simon_left_alive(self, ctx):
        simon_participant_role_id, simon_disqualified_role_id, simon_controller_role_id = await get_simon_says_roles(self, ctx)
        alive = ""
        alive_count = 0
        for mem in ctx.guild.members:
            if ctx.guild.get_role(simon_participant_role_id) in mem.roles:
                alive = str(mem.mention) + ", " + alive
                alive_count += 1
        alive = alive[:-1]
        if alive_count > 1:
            await ctx.send(embed=discord.Embed(title="Following are the Simon Says Participants that are still alive", description=alive, color=discord.Color.blue()))
        elif alive_count == 1:
            await ctx.send(embed=discord.Embed(title="Following is the last guy standing", description=alive, color=discord.Color.blue()))
        else:
            await ctx.send(embed=discord.Embed(title="Literally No one is alive it seems", color=discord.Color.red()))

    @commands.command(aliases=['simonkill', 'simon-kill', 'kill'])
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def simon_kill(self, ctx, *to_kill: discord.Member):
        simon_participant_role_id, simon_disqualified_role_id, simon_controller_role_id = await get_simon_says_roles(self, ctx)
        killed = ""

        if ctx.guild.get_role(simon_controller_role_id) in ctx.author.roles:
            for member in to_kill:
                if ctx.guild.get_role(simon_participant_role_id) not in member.roles:
                    killed = "\n" + killed + member.mention + " is already not alive"
                else:
                    await member.remove_roles(ctx.guild.get_role(simon_participant_role_id), reason="Killed by a simon says controller")
                    await member.add_roles(ctx.guild.get_role(simon_disqualified_role_id), reason="Killed by a simon says controller")
                    killed = "\n" + killed + member.mention
            await ctx.send(embed=discord.Embed(title="The following participants have been disqualified!", description=killed, color=discord.Color.green()))
        else:
            ctx.send(embed=discord.Embed(title="No, not you", description="Only users who have the <@&{}> role are allowed to use this command!".format(simon_controller_role_id),
                                         color=discord.Color.red()).set_footer("if you think that you are already having that role but still see this than contact Zacky#9543"))

    @simon_kill.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(embed=discord.Embed(title="Member not found", description="Try to do it again, but this time actually mention the people to kill", color=discord.Color.red()))
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=discord.Embed(title="Missing Permissions", description="Looks like I am missing out the `Manage Roles` Permissions to perform that operation!", color=discord.Color.red()))
        else:
            await ctx.author.send(error)

    @commands.command(aliases=['simonrevive', 'simon-revive', 'revive'])
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def simon_revive(self, ctx, *to_revive: discord.Member):
        simon_participant_role_id, simon_disqualified_role_id, simon_controller_role_id = await get_simon_says_roles(self, ctx)
        revived = ""

        if ctx.guild.get_role(simon_controller_role_id) in ctx.author.roles:
            for member in to_revive:
                if ctx.guild.get_role(simon_disqualified_role_id) not in member.roles:
                    revived = "\n" + revived + member.mention + " was already alive"
                else:
                    await member.remove_roles(ctx.guild.get_role(simon_disqualified_role_id), reason="revived by a simon says controller")
                    await member.add_roles(ctx.guild.get_role(simon_participant_role_id), reason="revived by a simon says controller")
                    revived = "\n" + revived + member.mention
            await ctx.send(embed=discord.Embed(title="The following participants have been revived!", description=revived, color=discord.Color.green()))
        else:
            ctx.send(embed=discord.Embed(title="No, not you", description="Only users who have the <@&{}> role are allowed to use this command!".format(simon_controller_role_id),
                                         color=discord.Color.red()).set_footer("if you think that you are already having that role but still see this than contact Zacky#9543"))

    @simon_revive.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(embed=discord.Embed(title="Member not found", description="Do it again, but this time actually mention the people to kill", color=discord.Color.red()))
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=discord.Embed(title="Missing Permissions", description="Looks like I am missing out the `Manage Roles` Permissions to perform that operation!", color=discord.Color.red()))
        else:
            await ctx.author.send(error)

    @commands.command(aliases=['simonpackup', 'simonresetroles', 'simonreset'])
    async def simon_clear_up(self, ctx):
        simon_participant_role_id, simon_disqualified_role_id, simon_controller_role_id = await get_simon_says_roles(self, ctx)
        if ctx.guild.get_role(simon_controller_role_id) in ctx.author.roles:
            for mem in ctx.guild.members:
                if ctx.guild.get_role(simon_participant_role_id) in mem.roles:
                    await mem.remove_roles(ctx.guild.get_role(simon_participant_role_id))
                if ctx.guild.get_role(simon_disqualified_role_id) in mem.roles:
                    await mem.remove_roles(ctx.guild.get_role(simon_disqualified_role_id))
            await ctx.send(embed=discord.Embed(title="Done", color=discord.Color.green()))
        else:
            await ctx.send(embed=discord.Embed(title="No, not you", description=f"Only users with the <@&{simon_controller_role_id}> role can do this.", color=discord.Color.red()))

    @commands.command(aliases=['SimonSaysSetup', 'simon-says-setup'])
    @commands.has_guild_permissions(manage_roles=True, manage_channels=True)
    async def simon_says_setup(self, ctx):
        id_list_to_save = {
            'roles': {},
            'channels': {}
        }

        def wait_for_reply_check(m):
            return m.author == ctx.message.author and m.channel == ctx.message.channel

        for role_to_set_for in ('simon_says_participant', 'simon_says_controller', 'simon_says_disqualified'):
            await ctx.send(embed=discord.Embed(description="Please tell me which role in this Server will belong to {}(s), Either mention it, or just Tell me the name of the role".format(role_to_set_for.replace("_", " ").capitalize()), color=discord.Color.from_hsv(random(), 1, 1)))
            message = await self.client.wait_for('message', check=wait_for_reply_check, timeout=120)

            if message.content.startswith("<@&"):
                role_id = int(message.content[3:-1])
                role = message.guild.get_role(role_id)
            else:
                for role in message.guild.roles:
                    if role.name == message.content:
                        break

            if role == None:
                await ctx.send(embed=discord.Embed(title='Failed!', description='Failed to recognise role (perhaps it doesn\'t exist?), please **only** tell me the role you would like to use (name should be case-sensitive)', color=discord.Color.from_hsv(random(), 1, 1)))
                return

            if ctx.message.author.roles[-1].position <= role.position:
                await ctx.send(embed=discord.Embed(description="<a:crossGif:760758713777913876> That role is higher than your highest role! or it doesn't exist", color=discord.Color.red()))
                return
            elif ctx.guild.get_member(self.client.user.id).roles[-1].position <= role.position:
                await ctx.send(embed=discord.Embed(description="<a:crossGif:760758713777913876> My highest role is lower then that role! or it doesn't exist", color=discord.Color.red()))
                return
            else:
                id_list_to_save['roles'][role_to_set_for] = role.id
                try:
                    await ctx.send(embed=discord.Embed(
                        title="<a:checkGif:760758712876400680> Success",
                        description=f"<@&{role.id}> is now set as the role for {role_to_set_for.replace('_', ' ').capitalize()}(s) <a:checkGif:760758712876400680> ",
                        color=discord.Color.green()
                    ))
                except:
                    await ctx.send(f"<a:checkGif:760758712876400680> {role.name} is now set as the role for {prettify_string(role_to_set_for)}(s).")

        # Simon Says Channel
        await ctx.send(embed=discord.Embed(description="Please tell me which channel in this Server will belong to hosting Simon Says event, please mention it.", color=discord.Color.red()))
        message = await self.client.wait_for('message', check=wait_for_reply_check, timeout=120)

        if message.content.startswith("<#"):
            channel_id = int(message.content[2:-1])
            channel = self.client.get_channel(channel_id)
        else:
            await ctx.send(embed=discord.Embed(
                title=f"{self.emojis['crossGif']} Failed",
                description="Please **mention** the channel you would like to use for hosting Simon Says events! (e.g. #simon-says)",
                color=discord.Color.red()
            ))
            return

        if channel == None:
            await ctx.send(embed=discord.Embed(description='Failed to recognise channel (perhaps it doesn\'t exist in this server? or perhaps I don\'t have to permissions to see it?), please **only** tell me the channel you would like to use', color=discord.Color.red()))
            return

        id_list_to_save['channels']['simon_says_channel'] = channel.id
        try:
            await ctx.send(embed=discord.Embed(
                title="<a:checkGif:760758712876400680> Success",
                description=f"<#{channel.id}> is now set as the channel for Simon Says Events! <a:checkGif:760758712876400680> ",
                color=discord.Color.green()
            ))
        except:
            await ctx.send(f"<#{channel.id}> is now set as the channel for Simon Says Events!")

        try:
            self.client.id_list['guild_setup_id_saves'][str(
                ctx.guild.id)]["simon_says"] = id_list_to_save
        except KeyError:
            self.client.id_list['guild_setup_id_saves'][str(ctx.guild.id)] = {
                "simon_says": id_list_to_save
            }

        await ctx.send(embed=discord.Embed(
            title=f"{self.emojis['checkGif']} Setup successful!",
            description=f"Here is a summary of the setup:\nSimon Says Participant Role: <@&{id_list_to_save['roles']['simon_says_participant']}>\nSimon Says Controller Role: <@&{id_list_to_save['roles']['simon_says_controller']}>\nDisqualified from Simon Says role: <@&{id_list_to_save['roles']['simon_says_disqualified']}>\nSimon Says Event Channel: <#{id_list_to_save['channels']['simon_says_channel']}>",
            color=discord.Color.green()
        ).set_footer(
            text="you can set these values again, by using the `-SimonSaysSetup` command again."
        ))

    @simon_says_setup.error
    async def clear_error(self, ctx, error):
        if isinstance(error, TimeoutError):
            await ctx.send("You spent too long to reply, please try again")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=discord.Embed(title="Missing Permissions", description="Looks like you are missing out on the `Manage Roles` and `Manage Channels` Permissions to perform that operation!", color=discord.Color.red()))
        else:
            raise error


def setup(client):
    client.add_cog(SimonSays(client))
