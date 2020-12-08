# -*- coding: UTF-8 -*-

import discord
from discord.ext import commands
from asyncio import TimeoutError
from random import random

initial_description = '''
:slight_smile: - **General Commands**
:clown: - **Simon Says Event Commands**
:tickets: - **Ticket System Commands**
:video_game: - **Fun Commands**
'''

help_general = """
`$p$help`:
Shows this help message

`$p$prefix`:
Change My Prefix

`$p$ping`: 
Get the bot's ping

`$p$invite`:
Invite me to your server!
or join our server!

`$p$report <issue to report>`:
Report an issue of this bot directly to the creator of this bot
`for e.g. $p$report Bot is very unstable`

`$p$suggest <suggestion>`:
Suggest some feature for this bot, directly to the creator of this bot
`for e.g. $p$suggest Please add more event hosting commands`

`$p$botInfo`:
Get information about this bot
"""

help_simon_says = """
`$p$SimonSaysStart <how long to accept participants>`:
Creates a participation message, which users can react to, to get the Simon Says Participation role.
This will only accept participants as long as the time you give
e.g. `$p$SimonSaysStart 5h 30m`

`$p$SimonSays`:
Say Something as Simon in the Simon Says Events Channel.
e.g. `$p$SimonSays person below will be killed!`

`$p$SimonKill`:
Disqualify Simon Says Participant(s).
e.g. `$p$SimonKill @PersonWhoFailed @AlsoAPersonWhoFailed`

`$p$SimonRevive`:
Revive Simon Says disqualified Participant(s).
e.g. `$p$SimonRevive @PersonWhoGetsAChance @another_person69`

`$p$SimonLeftAlive`:
Lists the number of simon says participant(s) that are still alive.

`$p$SimonReset`:
Removes the Simon Says Participant and Simon Says Disqualified roles from every member.

`$p$SimonSaysSetup`:
Setups your server to hold Simon Says Events.
"""

help_ticket_system = '''
`$p$New [reason]`:
Create a new ticket, reason is optional.
e.g. `$p$new Why is this bot so unstable??? HELP`

`$p$Add @<Role or User>`:
Add a role or a user to the private ticket.
e.g. `$p$add @DemoSupportMan`

`$p$Remove @<Role or User>`:
Some as `$p$add` but removes the user/role instead.
e.g. `$p$remove @AllBots`

`$p$Close [reason]`:
Close the current ticket with an optional reason.
e.g. `$p$close Solved this issue in #faq`

`$p$TicketSystemSetup`:
Setup your server to enable ticket system.
'''

help_fun_commands = '''
`$p$8Ball <TO PREDICT>`:
Predicts the outcome of your statement

`$p$RollDice`: 
Rolls a dice a tells the result

`$p$FlipCoin`:
Flip a coin

`$p$Meme`:
Sends a Meme

`$p$DankMeme`:
Sends a Meme from dankmemes subreddit

`$p$sendMemes <amount>`:
Same as `$p$Meme` but sends the memes in bulk and straight to your DM's, you can optionally say "dank" at the end to have the memes from dankmemes subreddit
`for e.g. $p$sendMemes 10 dank`
'''

help_embeds = {
    "\U0001F642": discord.Embed(  # 🙂 :slight_smile:
        title="General Commands",
        description=help_general
    ),
    "\U0001F921": discord.Embed(  # 🤡 :clown:
        title="Simon Says Commands",
        description=help_simon_says
    ),
    "\U0001F39F": discord.Embed(  # 🎟 :tickets:
        title="Ticket System Commands",
        description=help_ticket_system
    ),
    "\U0001F3AE": discord.Embed(  # 🎮 :video_game:
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
                    embed: discord.Embed = help_embeds[str(reaction.emoji)]
                except KeyError:
                    embed: discord.Embed = help_message.embeds[0]
                embed.description = embed.description.replace(
                    '$p$', self.client.prefix(self.client, ctx.message))
                embed.color = discord.Color.from_hsv(random(), 1, 1)
                embed.set_footer(
                    text="Please react below on one of the already reacted emojis for accessing categories")
                await help_message.edit(embed=embed)
                try:
                    await reaction.remove(user)
                except:
                    continue
            except TimeoutError:
                break


def setup(client):
    client.add_cog(HelpCommand(client))
