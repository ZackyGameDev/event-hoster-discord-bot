# -*- coding: UTF-8 -*-

import discord
from discord.ext import commands
from asyncio import TimeoutError
from random import random

initial_description = '''
:clown: **Simon Says Event Commands**
:tickets: **Ticket System Commands**
:video_game: **Fun Commands**
'''

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

help_fun_commands = '''
`8Ball <TO PREDICT>`:
Predicts the outcome of your statement

`RoleDice`: 
Roles a dice a tells the result

`FlipCoin`:
Flip a coin

`Meme`:
Sends a Meme

`DankMeme`:
Sends a Meme from dankmemes subreddit

`sendMemes <amount>`:
Same as `-Meme` but sends the memes in bulk and straight to your DM's, you can optionally say "dank" at the end to have the memes from dankmemes subreddit
`for e.g. -sendMemes 10 dank`
'''

help_embeds = {
    "\U0001F921" : discord.Embed(  # 🤡 :clown:
        title="Simon Says Commands",
        description=help_simon_says
    ),
    "\U0001F39F" : discord.Embed( # 🎟 :tickets:
        title="Ticket System Commands",
        description=help_ticket_system
    ),
    "\U0001F3AE" : discord.Embed( # 🎮 :video_game:
        title="Fun Commands",
        description=help_fun_commands
    )
}

class HelpCommand(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.client.remove_command("help")
    
    @commands.command()
    async def help(self, ctx):
        help_message = await ctx.send(embed=discord.Embed(title="React Below For Help", description=initial_description, color=discord.Color.gold()))
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
