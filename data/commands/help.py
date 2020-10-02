# -*- coding: UTF-8 -*-

import discord
from discord.ext import commands
from asyncio import TimeoutError
from random import random

help_simon_says = """
`SimonSays`:
Say Something as Simon in the Simon Says Events Channel.
e.g. `-SimonSays person below will be killed!`

`SimonKill`:
Disqualify Simon Says Participant(s).
e.g. `-SimonKill @PersonWhoFailed @AlsoAPersonWhoFailed`

`SimonRevive`:
Revive Simon Says disqualified Participant(s).
e.g. `-SimonRevive @PersonWhoGetsAChance @another_person69`

`SimonLeftAlive`:
Lists the number of simon says participant(s) that are still alive.

`SimonReset`:
Removes the Simon Says Participant and Simon Says Disqualified roles from every member.

`SimonSaysSetup`:
Setups your server to hold Simon Says Events.
"""

help_ticket_system = '''
`New [reason]`:
Create a new ticket, reason is optional.
e.g. `-new Why is this bot so unstable??? HELP`

`Add @<Role or User>`:
Add a role or a user to the private ticket.
e.g. `-add @DemoSupportMan`

`Remove @<Role or User>`:
Some as `-add` but removes the user/role instead.
e.g. `-remove @AllBots`

`Close [reason]`:
Close the current ticket with an optional reason.
e.g. `-close Solved this issue in #faq`

`TicketSystemSetup`:
Setup your server to enable ticket system.
'''

help_embeds = {
    "\U0001F389" : discord.Embed(  # 🎉
        title="Simon Says Commands",
        description=help_simon_says
    ),
    "\U0001F3AB" : discord.Embed( # 🎫
        title="Ticket System Commands",
        description=help_ticket_system
    )
}

class HelpCommand(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.client.remove_command("help")
    
    @commands.command()
    async def help(self, ctx):
        help_message = await ctx.send(embed=discord.Embed(description="Please React on one of the reactions on this message below", color=discord.Color.blue()))
        for emoji in help_embeds:
            await help_message.add_reaction(emoji)
        while True:
            def check(reaction, user, help_message=help_message):
                return user == ctx.message.author and reaction.message.id == help_message.id

            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout=600, check=check)
                try:
                    embed=help_embeds[str(reaction.emoji)]
                except KeyError:
                    await reaction.remove(user)
                    continue
                embed.color = discord.Color.from_hsv(random(), 1, 1)
                embed.set_footer(text="Please react below on one of the already reacted emojis for accessing categories")
                await help_message.edit(embed=embed)
                await reaction.remove(user)
            except TimeoutError:
                break
    
def setup(client):
    client.add_cog(HelpCommand(client))
