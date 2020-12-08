import discord
import json
from asyncio import TimeoutError
from discord.ext import commands
from data.utils.functions import prettify_string, read_file
from random import random


async def channel_is_ticket(self, ctx):
    channel_is_ticket = None
    try:
        async for entry in ctx.guild.audit_logs(limit=250, user=self.client.user, action=discord.AuditLogAction.channel_create):
            if ctx.channel.id == entry.target.id:
                channel_is_ticket = True
                break
            else:
                channel_is_ticket = False
    except:
        await ctx.send(embed=discord.Embed(
            title="Missing Permissions!",
            description="I need the permissions to the audit log to confirm that this channel is a ticket created by me and not a regular channel",
            color=discord.Color.red()
        ))
    if channel_is_ticket == None or channel_is_ticket == False:
        await ctx.send(embed=discord.Embed(
            title="Illegal Command!",
            description="This is not a ticket, hence cannot be closed with this command!",
            color=discord.Color.red()
        ).set_footer(
            text="if you think this is a mistake, please delete this channel manually"
        ))

    return channel_is_ticket


async def get_ticket_category_and_role(self, ctx):
    try:
        category_id = self.client.id_list['guild_setup_id_saves'][str(
            ctx.guild.id)]['ticket_system']['categories']['tickets_category']
        category = None
        for category in ctx.guild.categories:
            if category.id == category_id:
                break
            else:
                category = None

        staff_role_id = self.client.id_list['guild_setup_id_saves'][str(
            ctx.guild.id)]['ticket_system']['roles']['ticket_system_staff']

        return category, staff_role_id
    except KeyError:
        await ctx.send(embed=discord.Embed(
            title=f"{self.emojis['crossGif']} Failed",
            description=f"You have not yet setup this server by using the `-TicketSystemSetup` command to do that!",
            color=discord.Color.red()
        ).set_footer(
            text="If you think this is an error, contact Zacky#9543"
        ))


class TicketSystem(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.emojis = json.loads(read_file('id-list.json'))['emojis']

    @commands.command(aliases=["new", "newTicket", "new-ticket"])
    async def new_ticket(self, ctx, *, reason=None):
        new_tickets_category, staff_role_id = await get_ticket_category_and_role(self, ctx)

        new_ticket_channel_overwrites = {
            ctx.author: discord.PermissionOverwrite(read_messages=True),
            self.client.user: discord.PermissionOverwrite(read_messages=True, embed_links=True),
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.guild.get_role(staff_role_id): discord.PermissionOverwrite(read_messages=True)
        }

        try:
            tickets_count = self.client.id_list['tickets_count'][str(
                ctx.guild.id)]
        except KeyError:
            self.client.id_list['tickets_count'][str(ctx.guild.id)] = 0
            tickets_count = 0
        self.client.id_list['tickets_count'][str(ctx.guild.id)] += 1

        new_ticket = await new_tickets_category.create_text_channel(name=f"ticket-{tickets_count}", overwrites=new_ticket_channel_overwrites, reason=f'{reason} id:{ctx.author.id}')
        await new_ticket.send(embed=discord.Embed(
            description=f"Reason: `{reason}`",
            color=discord.Color.from_hsv(random(), 1, 1)
        ).set_author(
            name=f'{ctx.author} issued new ticket',
            icon_url=f'https://cdn.discordapp.com/avatars/{ctx.author.id}/{ctx.author.avatar}.png'
        ))
        await ctx.message.delete()
        await ctx.send(embed=discord.Embed(
            title="Ticket Created",
            description=f"I have created a new ticket for you <#{new_ticket.id}>,\n with Reason: `{reason}`",
            color=discord.Color.from_hsv(random(), 1, 1)
        ).set_author(
            name=f'{ctx.author}',
            icon_url=f'https://cdn.discordapp.com/avatars/{ctx.author.id}/{ctx.author.avatar}.png'
        ), delete_after=500)

    @new_ticket.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=discord.Embed(
                title="Missing Permissions!",
                description="I Am missing permissions to create channel!",
                color=discord.Color.red()
            ))
        else:
            await ctx.send(embed=discord.Embed(
                title="Something went wrong",
                description="Please report the following thing to Zacky#9543:\n`{}`".format(
                    str(error)),
                color=discord.Color.red()
            ))

    @commands.command(aliases=["add", "adduser", "add-user", "add_user", "add_role", "add-role", "addrole"])
    async def add_user_or_role(self, ctx, role_or_user):
        if await channel_is_ticket(self, ctx) == True:
            try:
                to_add_id = int(role_or_user[:-1][len(role_or_user)-19:])
            except:
                await ctx.send("Do that again, but actually @mention the role/user this time to add here")
            if "&" in role_or_user:
                to_add = ctx.guild.get_role(to_add_id)
            else:
                to_add = self.client.get_user(to_add_id)
            await ctx.channel.set_permissions(to_add, read_messages=True)
            await ctx.send(embed=discord.Embed(
                title="Success!",
                description="I have added {} to this ticket!".format(
                    role_or_user),
                color=discord.Color.green()
            ).set_author(
                name=f'{ctx.author}',
                icon_url=f'https://cdn.discordapp.com/avatars/{ctx.author.id}/{ctx.author.avatar}.png'
            ))

    @commands.command(aliases=["remove", "removeuser", "remove-user", "remove_user", "remove_role", "remove-role", "removerole"])
    async def remove_user_or_role(self, ctx, role_or_user):
        if await channel_is_ticket(self, ctx) == True:
            try:
                to_remove_id = int(role_or_user[:-1][len(role_or_user)-19:])
            except:
                await ctx.send("Do that again, but actually @mention the role/user this time to remove from here")
            if "&" in role_or_user:
                to_remove = ctx.guild.get_role(to_remove_id)
            else:
                to_remove = self.client.get_user(to_remove_id)
            await ctx.channel.set_permissions(to_remove, read_messages=False)
            await ctx.send(embed=discord.Embed(
                title="Success!",
                description="I have removed {} from this ticket!".format(
                    role_or_user),
                color=discord.Color.blue()
            ).set_author(
                name=f'{ctx.author}',
                icon_url=f'https://cdn.discordapp.com/avatars/{ctx.author.id}/{ctx.author.avatar}.png'
            ))

    @commands.command(aliases=["ticket_close", "closeticket", "close-ticket", "ticketclose", "ticket-close", "close"])
    async def close_ticket(self, ctx, *, reason=None):
        if await channel_is_ticket(self, ctx) == True:
            def wait_for_deny(message):
                return message.channel == ctx.channel

            async for entry in ctx.guild.audit_logs(limit=250, user=self.client.user, action=discord.AuditLogAction.channel_create):
                if ctx.channel.id == entry.target.id:
                    creator_id = int(entry.reason[-18:])
                    break

            try:
                await ctx.send(embed=discord.Embed(title="Closing ticket!", description="This ticket will be closed in **10 seconds**!\nIf you think this is a mistake, please send any message in this ticket!", color=discord.Color.blue()))
                message = await self.client.wait_for('message', check=wait_for_deny, timeout=10)
                await ctx.send("The deletion of this ticket has been stopped.")
            except TimeoutError:
                await ctx.channel.delete(reason="Ticket closed by {}, reason: `{}`".format(ctx.author, reason))
                await self.client.get_user(creator_id).send(embed=discord.Embed(
                    title="Your Ticket was closed",
                    description=f"Closed by {ctx.author},\nReason: `{reason}`",
                    color=discord.Color.from_hsv(random(), 1, 1)
                ))

    @close_ticket.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=discord.Embed(
                title="Missing Permissions!",
                description="I Am missing permissions to delete this channel!",
                color=discord.Color.red()
            ))
        else:
            await ctx.send(embed=discord.Embed(
                title="Something went wrong",
                description="Please report the following thing to Zacky#9543:\n`{}`".format(
                    str(error)),
                color=discord.Color.red()
            ))

    @commands.command(aliases=["ticketSystemSetup", "ticket-system-setup"])
    async def ticket_system_setup(self, ctx):
        id_list_to_save = {
            'roles': {},
            'categories': {}
        }

        def wait_for_reply_check(m):
            return m.author == ctx.message.author and m.channel == ctx.message.channel

        # Getting roles
        await ctx.send(embed=discord.Embed(description="Please tell me which role in this Server will belong to Ticket System Staff (the users that will have access to view all tickets), Either mention it, or just Tell me the name of the role", color=discord.Color.from_hsv(random(), 1, 1)))
        message = await self.client.wait_for('message', check=wait_for_reply_check, timeout=120)

        if message.content.startswith("<@&"):
            role_id = int(message.content[3:-1])
            role = message.guild.get_role(role_id)
        else:
            for role in message.guild.roles:
                if role.name == message.content:
                    break

        if role == None:
            await ctx.send(embed=discord.Embed(
                title='Failed',
                description='Failed to recognise role (perhaps it doesn\'t exist?), please **only** tell me the role you would like to use (name should be case-sensitive)',
                color=discord.Color.red()
            ))

        if ctx.message.author.roles[-1].position <= role.position:
            await ctx.send(embed=discord.Embed(description="<a:crossGif:760758713777913876> That role is higher than your highest role!", color=discord.Color.red()))
        elif ctx.guild.get_member(self.client.user.id).roles[-1].position <= role.position:
            await ctx.send(embed=discord.Embed(description="<a:crossGif:760758713777913876> My highest role is lower then that role!", color=discord.Color.red()))
        else:
            id_list_to_save['roles']['ticket_system_staff'] = role.id
            try:
                await ctx.send(embed=discord.Embed(
                    title="<a:checkGif:760758712876400680> Success",
                    description=f"<@&{role.id}> is now set as the role for Staff/Users that will have access to see all the tickets <a:checkGif:760758712876400680> ",
                    color=discord.Color.green()
                ))
            except:
                await ctx.send(f"<a:checkGif:760758712876400680> {role.name} is now set as the role for Staff/Users that will have access to see all the tickets.")

        # Tickets Category
        await ctx.send(embed=discord.Embed(description="Please tell me in which category I need to add the new tickets to. Just tell me the name of it.", color=discord.Color.from_hsv(random(), 1, 1)))
        message = await self.client.wait_for('message', check=wait_for_reply_check, timeout=120)

        category = None
        for category in ctx.guild.categories:
            if category.name.upper() == message.content.upper():
                break
            else:
                category = None

        if category == None:
            await ctx.send(embed=discord.Embed(
                title=f"{self.emojis['crossGif']} Failed",
                description="Please make sure that you are sending me the exact and correct name of the category. (this is case sensitive!)",
                color=discord.Color.red()
            ))

        id_list_to_save['categories']['tickets_category'] = category.id

        try:
            await ctx.send(embed=discord.Embed(
                title="<a:checkGif:760758712876400680> Success",
                description=f"{category.name} is now set as the Category for Creating new tickets in! <a:checkGif:760758712876400680> ",
                color=discord.Color.green()
            ))
        except:
            await ctx.send(f"<a:checkGif:760758712876400680> {category.name} is now set as the Category for Creating new tickets in!(s).")

        try:
            self.client.id_list['guild_setup_id_saves'][str(
                ctx.guild.id)]["ticket_system"] = id_list_to_save
        except KeyError:
            self.client.id_list['guild_setup_id_saves'][str(ctx.guild.id)] = {
                "ticket_system": id_list_to_save
            }

        await ctx.send(embed=discord.Embed(
            title=f"{self.emojis['checkGif']} Setup successful!",
            description=f"Here is a summary of the setup:\nTicket System Staff Role: <@&{id_list_to_save['roles']['ticket_system_staff']}>\nCategory to create new tickets in: {category.name}",
            color=discord.Color.green()
        ).set_footer(
            text="you can set these values again, by using the `-SimonSaysSetup` command again."
        ))


def setup(client):
    client.add_cog(TicketSystem(client))
