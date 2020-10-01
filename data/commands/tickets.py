import discord
import json
from discord.ext import commands
from data.utils.functions import prettify_string, read_file
from random import random

async def get_ticket_category_and_role(self, ctx):
    try:
        category_id = self.client.id_list['guild_setup_id_saves'][str(ctx.guild.id)]['ticket_system']['categories']['tickets_category']
        category = None
        for category in ctx.guild.categories:
            if category.id == category_id:
                break
            else:
                category = None

        staff_role_id = self.client.id_list['guild_setup_id_saves'][str(ctx.guild.id)]['ticket_system']['roles']['ticket_system_staff']

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
            ctx.author : discord.PermissionOverwrite(read_messages=True),
            self.client.user : discord.PermissionOverwrite(read_messages=True, embed_links=True),
            ctx.guild.default_role : discord.PermissionOverwrite(read_messages=False),
            ctx.guild.get_role(staff_role_id) : discord.PermissionOverwrite(read_messages=True)
        }
        
        try:
            tickets_count = self.client.id_list['tickets_count'][str(ctx.guild.id)]
        except KeyError:
            self.client.id_list['tickets_count'][str(ctx.guild.id)] = 0
            tickets_count = 0
        self.client.id_list['tickets_count'][str(ctx.guild.id)] += 1
        
        new_ticket = await new_tickets_category.create_text_channel(name=f"ticket-{tickets_count}", overwrites=new_ticket_channel_overwrites, reason=reason)
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
    
    @commands.command(aliases=["ticketSystemSetup", "ticket-system-setup"])
    async def ticket_system_setup(self, ctx):
        id_list_to_save = {
            'roles' : {},
            'categories' : {}
        }
        
        def wait_for_reply_check(m):
            return m.author == ctx.message.author and m.channel == ctx.message.channel
        
        while True:
            await ctx.send("Please tell me which role in this Server will belong to Ticket System Staff (the users that will have access to view all tickets), Either mention it, or just Tell me the name of the role")
            message = await self.client.wait_for('message', check=wait_for_reply_check, timeout=120)
            
            if message.content.startswith("<@&"):
                role_id = int(message.content[3:-1])
                role = message.guild.get_role(role_id)
            else:
                for role in message.guild.roles:
                    if role.name == message.content:
                        break

            if role == None:
                await ctx.send('Failed to recognise role (perhaps it doesn\'t exist?), please **only** tell me the role you would like to use (name should be case-sensitive)')
                continue
        
            if ctx.message.author.roles[-1].position <= role.position:
                await ctx.send("<a:crossGif:760758713777913876> That role is higher than your highest role!")
            elif ctx.guild.get_member(self.client.user.id).roles[-1].position <= role.position:
                await ctx.send("<a:crossGif:760758713777913876> My highest role is lower then that role!")
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
                break
    
        # Tickets Category
        while True:
            await ctx.send("Please tell me in which category I need to add the new tickets to. Just tell me the name of it.")
            message = await self.client.wait_for('message', check=wait_for_reply_check, timeout=120)
            
            category = None
            for category in ctx.guild.categories:
                if category.name.upper() == message.content.upper():
                    break
                else:
                    category = None

            if category == None :
                await ctx.send(embed=discord.Embed(
                    title=f"{self.emojis['crossGif']} Failed",
                    description="Please make sure that you are sending me the exact and correct name of the category. (this is case sensitive!)",
                    color=discord.Color.red()
                ))
                continue

            id_list_to_save['categories']['tickets_category'] = category.id
            
            try:
                await ctx.send(embed=discord.Embed(
                    title="<a:checkGif:760758712876400680> Success", 
                    description=f"{category.name} is now set as the Category for Creating new tickets in! <a:checkGif:760758712876400680> ",
                    color=discord.Color.green()
                ))
            except:
                await ctx.send(f"<a:checkGif:760758712876400680> {category.name} is now set as the Category for Creating new tickets in!(s).")            
            break
        
        try:
            self.client.id_list['guild_setup_id_saves'][str(ctx.guild.id)]["ticket_system"].update(id_list_to_save)
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