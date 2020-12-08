import discord

from discord.ext import commands
from random import random


class ModerationCommands(commands.Cog):

    def __init__(self, client):
        self.client = client

    def cant_ban_user_responses(self, ctx):
        return {
            self.client.user.id: discord.Embed(
                description='no u',
                color=discord.Color.red()
            ),
            ctx.author.id: discord.Embed(
                title="Seriously?",
                description='Are you seriously gonna ban **yourself**',
                color=discord.Color.red()
            )
        }

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member_to_ban: discord.Member, *, reason='None'):

        if member_to_ban.id in self.cant_ban_user_responses(ctx):
            await ctx.send(embed=self.cant_ban_user_responses(ctx)[member_to_ban.id])
            return

        if len(reason) > 150:
            await ctx.send('human thats a long reason keep it under 150 characters')
            return

        await member_to_ban.ban(reason=reason)

        try:
            await ctx.send(embed=discord.Embed(
                title=f'{member_to_ban} has been Banned',
                description=f"Reason: `{reason}`",
                color=discord.Color.from_hsv(random(), 1, 1)
            ).set_author(
                name=f'{ctx.author}',
                icon_url=f'https://cdn.discordapp.com/avatars/{ctx.author.id}/{ctx.author.avatar}.png'
            ))
        except discord.Forbidden:
            try:
                await ctx.send(f'Banned {member_to_ban} with reason: {reason}.\nAlso give me the perms to send embeds in here sending raw content looks bland')
            except:
                await ctx.author.send(f'Banned {member_to_ban} with reason: {reason}.\nAlso Come on, give me the perms to message in the server like bruh.')

    @ban.error
    async def handle_error(self, ctx, error):
        if isinstance(error, commands.Forbidden) or isinstance(error, commands.BotMissingPermissions):
            await ctx.send(embed=discord.Embed(
                title='🚫 Bot Missing Permissions!',
                description='Looks like I\'m missing out on the ***`Ban Members`*** Permissions to perform this task',
                color=discord.Color.red()
            ))
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=discord.Embed(
                title='🚫 Missing Permissions',
                description='You don\'t have the ***`Ban Members`*** Permission to do this',
                color=discord.Color.red()
            ))
        elif isinstance(error, commands.ConversionError):
            await ctx.send('do that again, but this time mention the person to ban')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=discord.Embed(
                title="Missing Arguments!",
                description="Please mention the person to ban!\nFor e.g. `z!ban @RuleBreaker [optional reason here]`",
                color=discord.Color.red()
            ))

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member_to_kick: discord.Member, *, reason='None'):

        if member_to_kick.id in self.cant_ban_user_responses(ctx):
            await ctx.send(embed=self.cant_ban_user_responses(ctx)[member_to_kick.id].replace('ban', 'kick'))
            return

        if len(reason) > 150:
            await ctx.send('human thats a long reason keep it under 150 characters')
            return

        await member_to_kick.kick(reason=reason)

        try:
            await ctx.send(embed=discord.Embed(
                title=f'{member_to_kick} has been Kicked',
                description=f"Reason: `{reason}`",
                color=discord.Color.from_hsv(random(), 1, 1)
            ).set_author(
                name=f'{ctx.author}',
                icon_url=f'https://cdn.discordapp.com/avatars/{ctx.author.id}/{ctx.author.avatar}.png'
            ))
        except discord.Forbidden:
            try:
                await ctx.send(f'Kicked {member_to_kick} with reason: {reason}.\nAlso give me the perms to send embeds in here sending raw content looks bland')
            except:
                await ctx.author.send(f'Kicked {member_to_kick} with reason: {reason}.\nAlso Come on, give me the perms to message in the server like bruh.')

    @kick.error
    async def handle_error(self, ctx, error):
        if isinstance(error, commands.Forbidden) or isinstance(error, commands.BotMissingPermissions):
            await ctx.send(embed=discord.Embed(
                title='🚫 Bot Missing Permissions!',
                description='Looks like I\'m missing out on the ***`Kick Members`*** Permissions to perform this task',
                color=discord.Color.red()
            ))
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=discord.Embed(
                title='🚫 Missing Permissions',
                description='You don\'t have the ***`Kick Members`*** Permission to do this',
                color=discord.Color.red()
            ))
        elif isinstance(error, commands.ConversionError):
            await ctx.send('do that again, but this time mention the person to kick')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=discord.Embed(
                title="Missing Arguments!",
                description="Please mention the person to kick!\nFor e.g. `z!kick @RuleBreaker [Optional reason here]`",
                color=discord.Color.red()
            ))

    @commands.command(aliases=['revokeBan'])
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, user_to_unban: str):
        try:
            user_to_unban_name, user_to_unban_discriminator = user_to_unban.split(
                '#')
        except:
            await ctx.send('Please send the user to unban in the following format: `UserName#FourDigitTag`')
            return

        banned_users = await ctx.guild.bans()
        for ban_entry in banned_users:
            if (ban_entry.user.name, ban_entry.user.discriminator) == (user_to_unban_name, user_to_unban_discriminator):
                await ctx.guild.unban(ban_entry.user)
                try:
                    await ctx.send(embed=discord.Embed(
                        title=f"Ban from {ban_entry.user} revoked",
                        description=f"by {str(ctx.author)}",
                        color=discord.Color.green()
                    ))
                except:
                    await ctx.send(f"Ban from {ban_entry.user} revoked\nalso why don't i have the perm to send embeds in here? sending bland text isn't cool enough, alright?")
                else:
                    await ctx.author.send(embed=discord.Embed(
                        title=f"Ban from {ban_entry.user} revoked",
                        description=f"Also give me the Permissions to send messages in the server like come on human!",
                        color=discord.Color.green()
                    ))

    @unban.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=discord.Embed(
                title="Missing Arguments!",
                description="Please send the **username** 4 digit **Tag** or **Discriminator** of the user to unban\n**for e.g.**\n~~`z!unban InnocentGuy`~~\n`z!unban InnocentGuy#6969`",
                color=discord.Color.red()
            ))
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=discord.Embed(
                title='Missing Permissions!',
                description="Only the members who already have the permission to ***`Ban Members`*** are allowed to use this command",
                color=discord.Color.red()
            ))


def setup(client):
    client.add_cog(ModerationCommands(client))
